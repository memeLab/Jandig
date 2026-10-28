import hashlib
from os.path import basename, splitext

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile, UploadedFile
from django.forms.widgets import NumberInput
from django.template import loader
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from PIL import Image, UnidentifiedImageError

from core.marker_utils import (
    MAX_SVG_ASPECT_RATIO,
    SvgAspectRatioError,
    SvgTooComplexError,
    generate_marker_variants,
    is_svg,
    rasterize_svg,
    strip_existing_border,
)
from core.media_dimensions import extract_dimensions
from core.models import Artwork, Marker, ObjectExtensions, Feedback
from core.upload_limits import (
    AUDIO,
    OBJECT_KIND_BY_EXTENSION,
    RASTER_MARKER,
    SVG_MARKER,
    THUMBNAIL,
    upload_size_error,
)

from .models import Exhibit, ExhibitTypes, Object, Sound

DEFAULT_AUTHOR_PLACEHOLDER = "declare different author name"


def _sha256(file):
    digest = hashlib.sha256()
    for chunk in file.chunks():
        digest.update(chunk)
    file.seek(0)  # Reset file pointer
    return digest.digest()


def file_has_changed(new_file, instance_file):
    # Editing without replacing the file hands back the stored file itself.
    if new_file is instance_file:
        return False
    # Comparing sizes first avoids downloading the stored file at all when
    # they differ; otherwise both are hashed chunk by chunk instead of being
    # read whole into memory.
    if new_file.size != instance_file.size:
        return True
    return _sha256(new_file) != _sha256(instance_file)


class RangeInput(NumberInput):
    input_type = "range"


class ExhibitSelectForm(forms.Form):
    exhibit = forms.ModelChoiceField(
        queryset=Exhibit.objects.filter(exhibit_type=ExhibitTypes.AR).order_by("name")
    )

    def __init__(self, *args, search=None, **kwargs):
        """`search` narrows thelist server-side so long lists stay usable."""
        super().__init__(*args, **kwargs)
        if search:
            self.fields["exhibit"].queryset = self.fields["exhibit"].queryset.filter(
                name__icontains=search
            )


class ObjectWidget(forms.ClearableFileInput):
    """Custom widget for displaying an object correctly on edit forms if it is an image or video."""

    template_name = "core/templates/object_edit_template.jinja2"
    thumbnail = None

    def __init__(self, thumbnail=None, attrs=None):
        super().__init__(attrs)
        self.thumbnail = thumbnail

    def render(self, name, value, attrs=None, renderer=None):
        attrs.update({"accept": ".gif, .png, .mp4, .webm, .glb"})
        context = self.get_context(name, value, attrs)
        if self.thumbnail:
            context["widget"]["thumbnail"] = self.thumbnail

        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)


# Feedback attachments come from anonymous visitors, so keep them small.
MAX_FEEDBACK_ATTACHMENT_BYTES = 5 * 1024 * 1024
# Markers are rasterised and uploaded to the AR viewer as textures, so an
# upload far larger than a 4K texture costs storage and marker-generation time
# without improving detection. Both sides are capped at this value.
MAX_MARKER_DIMENSION = 4096


class UploadObjectForm(forms.ModelForm):
    selected_sound = forms.ModelChoiceField(
        queryset=Sound.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super(UploadObjectForm, self).__init__(*args, **kwargs)

        if thumbnail := kwargs.get("initial", {}).get("thumbnail", None):
            self.fields["source"].widget = ObjectWidget(thumbnail)
        else:
            self.fields["source"].widget = ObjectWidget()

        self.fields["author"].widget.attrs["placeholder"] = _(
            "declare different author name"
        )

        self.fields["title"].widget.attrs["placeholder"] = _("Object's title")

    class Meta:
        model = Object
        fields = ("source", "author", "title", "thumbnail", "audio_description")

    def clean_source(self):
        file = self.cleaned_data.get("source")

        allowed_extensions = ["gif", "png", "mp4", "webm", "glb"]
        extension = getattr(file, "name", "").split(".")[-1].lower()
        if extension not in allowed_extensions:
            raise forms.ValidationError(
                _(
                    "Only GIF images, PNG images, MP4, WebM videos, and GLB files are allowed."
                )
            )
        if error := upload_size_error(file, OBJECT_KIND_BY_EXTENSION[extension]):
            raise forms.ValidationError(error)
        # Object already exists, we need to check if it's being used by another user
        if self.instance.pk:
            if file_has_changed(file, self.instance.source):
                if self.instance.is_used_by_other_user:
                    raise forms.ValidationError(
                        _(
                            "This object is being used by another user. You cannot change the source file."
                        )
                    )

        return file

    def clean_thumbnail(self):
        file = self.cleaned_data.get("thumbnail")
        # Only a fresh upload is checked; a stored thumbnail is handed back
        # as is when the object is edited without a new one.
        if not isinstance(file, UploadedFile):
            return file
        if error := upload_size_error(file, THUMBNAIL):
            raise forms.ValidationError(error)
        # The ImageField has already opened (but not decoded) the image.
        width, height = file.image.size
        limit = settings.MAX_THUMBNAIL_DIMENSION
        if width > limit or height > limit:
            raise forms.ValidationError(
                _(
                    "The thumbnail generated for this model is %(width)sx"
                    "%(height)s pixels. Thumbnails are limited to %(limit)sx"
                    "%(limit)s pixels, so please reload the page and upload "
                    "the model again."
                ),
                params={"width": width, "height": height, "limit": limit},
            )
        return file

    def clean_audio_description(self):
        file = self.cleaned_data.get("audio_description")
        if not file:
            return None

        allowed_extensions = ["mp3", "ogg", "wav"]
        extension = getattr(file, "name", "").split(".")[-1].lower()
        if extension not in allowed_extensions:
            raise forms.ValidationError(
                _("Only MP3, OGG, and WAV audio files are allowed.")
            )
        if error := upload_size_error(file, AUDIO):
            raise forms.ValidationError(error)
        return file

    def save(self, *args, **kwargs):
        self.instance.sound = self.cleaned_data.get("selected_sound", None)
        self.instance.file_size = self.instance.source.size
        self.instance.file_name_original = self.instance.source.name.split("/")[-1]
        self.instance.file_extension = self.instance.source.name.split(".")[-1].lower()

        thumbnail = self.cleaned_data.get("thumbnail") or self.instance.thumbnail
        dims = extract_dimensions(
            self.instance.source, self.instance.file_extension, thumbnail
        )
        if dims:
            self.instance.width, self.instance.height = dims

        return super(UploadObjectForm, self).save(*args, **kwargs)


class UploadMarkerForm(forms.ModelForm):
    inner_border = forms.BooleanField(
        required=False,
        label=_("Add inner border"),
    )
    # Override the model's ImageField with a plain FileField. ImageField
    # would reject anything Pillow can't open (notably SVG); we want to
    # accept SVG and rasterise it ourselves before the rest of the
    # pipeline runs.
    source = forms.FileField()
    remove_existing_border = forms.BooleanField(
        required=False,
        label=_("Remove existing border"),
        help_text=_(
            "Tick this if your image already has a marker border, so a second "
            "one is not drawn around it."
        ),
    )

    def __init__(self, *args, **kwargs):
        super(UploadMarkerForm, self).__init__(*args, **kwargs)
        self.fields["author"].widget.attrs["placeholder"] = _(
            DEFAULT_AUTHOR_PLACEHOLDER
        )
        self.fields["title"].widget.attrs["placeholder"] = _("Marker's title")

    class Meta:
        model = Marker
        fields = ("source", "author", "title")

    def clean_source(self):
        file = self.cleaned_data.get("source")
        if file is None:
            raise forms.ValidationError(_("This field is required."))
        if getattr(file, "name", None):
            file.name = basename(file.name)

        if error := upload_size_error(
            file, SVG_MARKER if is_svg(file.name) else RASTER_MARKER
        ):
            raise forms.ValidationError(error)

        if is_svg(file.name):
            stem, _extension = splitext(file.name)
            try:
                file.seek(0)
                png_bytes = rasterize_svg(file.read())
            except SvgAspectRatioError:
                raise forms.ValidationError(
                    _(
                        "This SVG is too long and thin to work as a marker. Its "
                        "longest side can be at most %(ratio)s times its "
                        "shortest side."
                    ),
                    params={"ratio": MAX_SVG_ASPECT_RATIO},
                )
            except SvgTooComplexError:
                raise forms.ValidationError(
                    _(
                        "This SVG is too complex to turn into a marker. Simplify "
                        "it, or export it as a PNG or JPG and upload that instead."
                    )
                )
            except ValueError:
                raise forms.ValidationError(
                    _("Could not render SVG. Make sure the file is a valid SVG.")
                )
            # Fall through so the raster gets the same checks as any upload.
            # rasterize_svg already fits it within SVG_RASTER_WIDTH, well under
            # MAX_MARKER_DIMENSION, so for SVGs the size check is a backstop.
            file = SimpleUploadedFile(
                name=f"{stem}.png",
                content=png_bytes,
                content_type="image/png",
            )

        try:
            file.seek(0)
            with Image.open(file) as image:
                width, height = image.size
                image.verify()
            file.seek(0)
        except (UnidentifiedImageError, OSError):
            raise forms.ValidationError(
                _("Upload a valid image. Supported formats: PNG, JPG, GIF, SVG.")
            )

        # Only a fresh upload is checked. Editing a marker without replacing
        # the file hands back the stored file, which may predate the limit.
        if isinstance(file, UploadedFile) and (
            width > MAX_MARKER_DIMENSION or height > MAX_MARKER_DIMENSION
        ):
            raise forms.ValidationError(
                _(
                    "This image is %(width)sx%(height)s pixels. Markers are limited "
                    "to %(limit)sx%(limit)s pixels, so please resize it before "
                    "uploading."
                ),
                params={
                    "width": width,
                    "height": height,
                    "limit": MAX_MARKER_DIMENSION,
                },
            )
        return file

    def save(self, *args, **kwargs):
        commit = kwargs.get("commit", True)
        instance = super(UploadMarkerForm, self).save(*args, **kwargs)
        if commit:
            if self.cleaned_data.get("remove_existing_border", False):
                strip_existing_border(instance)
            generate_marker_variants(
                instance,
                inner_border=self.cleaned_data.get("inner_border", False),
            )
        return instance


class ArtworkForm(forms.ModelForm):
    selected_marker = forms.ModelChoiceField(
        queryset=Marker.objects.all(),
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    selected_object = forms.ModelChoiceField(
        queryset=Object.objects.exclude(file_extension=ObjectExtensions.GLB),
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    scale = forms.FloatField(
        min_value=0.1,
        max_value=5.0,
        initial=1.0,
        widget=RangeInput(attrs={"class": "slider", "step": "0.1"}),
    )
    selected_sound = forms.ModelChoiceField(
        queryset=Sound.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Artwork
        fields = ["title", "description", "position_x", "position_y"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": _("Artwork title")}
            ),
            "description": forms.Textarea(
                attrs={"class": "form-control", "placeholder": _("Artwork description")}
            ),
            "position_x": RangeInput(
                attrs={"class": "slider", "step": "0.1", "min": "-2.0", "max": "2.0"}
            ),
            "position_y": RangeInput(
                attrs={"class": "slider", "step": "0.1", "min": "-2.0", "max": "2.0"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super(ArtworkForm, self).__init__(*args, **kwargs)

        if self.instance.pk:
            # If editing an existing artwork, prepopulate the fields
            self.fields["scale"].initial = self.instance.scale_x
            self.fields["selected_marker"].initial = self.instance.marker
            self.fields["selected_object"].initial = self.instance.augmented
            self.fields["selected_sound"].initial = self.instance.sound

    def clean_position_x(self):
        position_x = self.cleaned_data.get("position_x")
        if position_x is not None:
            if position_x < -2.0:
                raise forms.ValidationError(_("Position X must be at least -2.0"))
            if position_x > 2.0:
                raise forms.ValidationError(_("Position X must not exceed 2.0"))
        return position_x

    def clean_position_y(self):
        position_y = self.cleaned_data.get("position_y")
        if position_y is not None:
            if position_y < -2.0:
                raise forms.ValidationError(_("Position Y must be at least -2.0"))
            if position_y > 2.0:
                raise forms.ValidationError(_("Position Y must not exceed 2.0"))
        return position_y

    def save(self, commit=True):
        artwork = super().save(commit=False)
        artwork.marker = self.cleaned_data["selected_marker"]
        artwork.augmented = self.cleaned_data["selected_object"]
        artwork.sound = self.cleaned_data["selected_sound"]
        artwork.scale_x = self.cleaned_data["scale"]
        artwork.scale_y = self.cleaned_data["scale"]
        return artwork


class ExhibitForm(forms.ModelForm):
    artworks = forms.CharField(max_length=1000, required=False)
    augmenteds = forms.CharField(max_length=1000, required=False)
    sounds = forms.CharField(max_length=1000, required=False)

    def __init__(self, *args, exhibit_type=None, **kwargs):
        super(ExhibitForm, self).__init__(*args, **kwargs)
        self.fields["name"].widget.attrs["placeholder"] = _("Exhibit Title")
        self.fields["slug"].widget.attrs["placeholder"] = _(
            "Complete with your Exhibit URL here"
        )
        # The route picks the exhibit type for create; for edit, the
        # existing instance's type is authoritative.
        if exhibit_type is None and self.instance.pk:
            exhibit_type = self.instance.exhibit_type
        self.exhibit_type = exhibit_type
        # On edit, pre-populate the hidden M2M inputs with the current
        # selections so a user who only changes name/URL doesn't end
        # up posting empty strings that clobber the data. The JS in
        # exhibit_create_*.jinja2 still rewrites the input on click.
        if self.instance.pk:
            self.fields["artworks"].initial = ",".join(
                str(a.id) for a in self.instance.artworks.all()
            )
            self.fields["augmenteds"].initial = ",".join(
                str(o.id) for o in self.instance.augmenteds.all()
            )
            self.fields["sounds"].initial = ",".join(
                str(s.id) for s in self.instance.sounds.all()
            )

    class Meta:
        model = Exhibit
        fields = ("name", "slug", "artworks", "augmenteds")
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": _("Exhibit Title")}),
            "slug": forms.TextInput(
                attrs={"placeholder": _("Complete with your Exhibit URL here")}
            ),
        }

    def clean_name(self):
        name = self.cleaned_data["name"]
        qs = Exhibit.objects.filter(name=name)
        if self.instance.pk:
            qs = qs.exclude(id=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                _(
                    "This name is already being used. Please choose another name for your exhibit."
                )
            )
        return name

    def clean_slug(self):
        slug = self.cleaned_data["slug"]
        qs = Exhibit.objects.filter(slug=slug)
        if self.instance.pk:
            qs = qs.exclude(id=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                _(
                    "That exhibit slug is already in use. Please choose another slug for your exhibit."
                )
            )
        return slug

    def clean_artworks(self):
        artworks_str = self.cleaned_data.get("artworks", "")
        if not artworks_str:
            return []

        artwork_ids = [id.strip() for id in artworks_str.split(",") if id.strip()]
        try:
            artwork_ids = [int(id) for id in artwork_ids]
        except ValueError:
            raise forms.ValidationError(_("Invalid artwork IDs provided."))

        artworks = list(Artwork.objects.filter(id__in=artwork_ids).order_by("-id"))
        return artworks

    def clean_augmenteds(self):
        augmenteds_str = self.cleaned_data.get("augmenteds", "")
        if not augmenteds_str:
            return []

        augmented_ids = [id.strip() for id in augmenteds_str.split(",") if id.strip()]
        try:
            augmented_ids = [int(id) for id in augmented_ids]
        except ValueError:
            raise forms.ValidationError(_("Invalid object IDs provided."))

        augmenteds = list(Object.objects.filter(id__in=augmented_ids).order_by("-id"))
        return augmenteds

    def clean_sounds(self):
        sounds_str = self.cleaned_data.get("sounds", "")
        if not sounds_str:
            return []

        sound_ids = [id.strip() for id in sounds_str.split(",") if id.strip()]
        try:
            sound_ids = [int(id) for id in sound_ids]
        except ValueError:
            raise forms.ValidationError(_("Invalid sound IDs provided."))

        sounds = list(Sound.objects.filter(id__in=sound_ids).order_by("-id"))
        return sounds

    def clean(self):
        cleaned_data = super().clean()
        artworks = cleaned_data.get("artworks") or []
        augmenteds = cleaned_data.get("augmenteds") or []

        # The route (/exhibits/create-ar/ vs /create-mr/) selected the
        # exhibit type. Validate the relevant content list — AR requires
        # artworks, MR requires augmented objects.
        if self.exhibit_type == ExhibitTypes.AR and not artworks:
            raise forms.ValidationError(_("AR exhibits require at least one artwork."))
        if self.exhibit_type == ExhibitTypes.MR and not augmenteds:
            raise forms.ValidationError(
                _("MR exhibits require at least one augmented object.")
            )
        # Fallback for callers that didn't pass exhibit_type — keep
        # the old "you must pick at least something" guard.
        if self.exhibit_type is None and not artworks and not augmenteds:
            raise forms.ValidationError(
                _("You must select at least one artwork or augmented object.")
            )

        return cleaned_data

    def save(self, commit=True):
        exhibit = super().save(commit=False)

        artworks = self.cleaned_data.get("artworks", [])
        augmenteds = self.cleaned_data.get("augmenteds", [])
        sounds = self.cleaned_data.get("sounds", [])

        # The exhibit type comes from the route (create) or the existing
        # row (edit), set in __init__. Only fall back to inferring from
        # the data if no type was supplied — protects against callers
        # that haven't been updated.
        if self.exhibit_type is not None:
            exhibit.exhibit_type = self.exhibit_type
        else:
            exhibit.exhibit_type = ExhibitTypes.MR if augmenteds else ExhibitTypes.AR

        if commit:
            exhibit.save()
            exhibit.artworks.set(artworks)
            exhibit.augmenteds.set(augmenteds)
            exhibit.sounds.set(sounds)

        return exhibit


class SoundForm(forms.ModelForm):
    class Meta:
        model = Sound
        fields = ("title", "file", "author")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file"].widget.attrs.update(
            {"accept": ".mp3,.ogg,.wav", "style": "height: auto;"}
        )

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if not file:
            raise forms.ValidationError(_("This field is required."))

        allowed_extensions = ["mp3", "ogg", "wav"]
        extension = getattr(file, "name", "").split(".")[-1].lower()
        if extension not in allowed_extensions:
            raise forms.ValidationError(
                _("Only MP3, OGG, and WAV audio files are allowed.")
            )
        if error := upload_size_error(file, AUDIO):
            raise forms.ValidationError(error)

        # Sound already exists, we need to check if it's being used by another user
        if self.instance.pk:
            if file_has_changed(file, self.instance.file):
                if self.instance.is_used_by_other_user:
                    raise forms.ValidationError(
                        _(
                            "This sound is being used by another user. You cannot change the source file."
                        )
                    )

        return file

    def save(self, *args, **kwargs):
        if owner := kwargs.get("owner", None):
            self.instance.owner = owner
            del kwargs["owner"]

        self.instance.file_size = self.instance.file.size
        self.instance.file_name_original = self.instance.file.name.split("/")[-1]
        self.instance.file_extension = self.instance.file.name.split(".")[-1].lower()

        return super(SoundForm, self).save(*args, **kwargs)


class FeedbackForm(forms.ModelForm):
    """Public bug report / feature request form linked from the footer."""

    class Meta:
        model = Feedback
        fields = ("kind", "description", "email", "attachment")
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 6,
                    "placeholder": _("What happened, and what did you expect?"),
                }
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": _("Your e-mail (optional, so we can reply)")}
            ),
        }

    def clean_attachment(self):
        attachment = self.cleaned_data.get("attachment")
        if not attachment:
            return None

        allowed_extensions = ["png", "jpg", "jpeg", "gif", "webp", "pdf", "txt", "log"]
        extension = getattr(attachment, "name", "").split(".")[-1].lower()
        if extension not in allowed_extensions:
            raise forms.ValidationError(
                _("Attach a screenshot (PNG, JPG, GIF, WebP), a PDF or a text log.")
            )
        if attachment.size > MAX_FEEDBACK_ATTACHMENT_BYTES:
            raise forms.ValidationError(
                _("Attachments are limited to %(limit)s MB."),
                params={"limit": MAX_FEEDBACK_ATTACHMENT_BYTES // (1024 * 1024)},
            )
        return attachment
