import re
from io import BytesIO

from django import forms
from django.core.files.base import ContentFile, File
from django.forms.widgets import NumberInput
from django.template import loader
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from PIL import Image
from pymarker.core import generate_patt_from_image

from core.models import Artwork, Marker, ObjectExtensions
from core.views.api_views import MarkerGeneratorAPIView

from .models import Exhibit, ExhibitTypes, Object, Sound

DEFAULT_AUTHOR_PLACEHOLDER = "declare different author name"


class RangeInput(NumberInput):
    input_type = "range"


class ExhibitSelectForm(forms.Form):
    exhibit = forms.ModelChoiceField(
        queryset=Exhibit.objects.filter(exhibit_type=ExhibitTypes.AR).order_by("name")
    )


class ObjectWidget(forms.ClearableFileInput):
    """Custom widget for displaying an object correctly on edit forms if it is an image or video."""

    template_name = "core/templates/object_edit_template.jinja2"
    thumbnail = None

    def __init__(self, thumbnail=None, attrs=None):
        super().__init__(attrs)
        self.thumbnail = thumbnail

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        if self.thumbnail:
            context["widget"]["thumbnail"] = self.thumbnail
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)


class UploadObjectForm(forms.ModelForm):
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
        fields = ("source", "author", "title", "thumbnail")

    def clean_source(self):
        file = self.cleaned_data.get("source")
        if not file:
            raise forms.ValidationError(_("This field is required."))

        allowed_extensions = ["gif", "mp4", "webm", "glb"]
        extension = getattr(file, "name", "").split(".")[-1].lower()
        if extension not in allowed_extensions:
            raise forms.ValidationError(
                _("Only GIF images, MP4, WebM videos, and GLB files are allowed.")
            )
        # Object already exists, we need to check if it's being used by another user
        if self.instance.pk:
            # Compare if the file changed
            file_content = file.read()
            file.seek(0)  # Reset file pointer
            instance_content = self.instance.source.read()
            self.instance.source.seek(0)  # Reset instance file pointer

            if instance_content != file_content:
                if self.instance.is_used_by_other_user():
                    raise forms.ValidationError(
                        _(
                            "This object is being used by another user. You cannot change the source file."
                        )
                    )

        return file

    def save(self, *args, **kwargs):
        if owner := kwargs.get("owner", None):
            self.instance.owner = owner
            del kwargs["owner"]

        self.instance.file_size = self.instance.source.size
        self.instance.file_name_original = self.instance.source.name.split("/")[-1]
        self.instance.file_extension = self.instance.source.name.split(".")[-1].lower()

        return super(UploadObjectForm, self).save(*args, **kwargs)


class UploadMarkerForm(forms.ModelForm):
    inner_border = forms.BooleanField(
        required=False,
        label=_("Add inner border"),
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

    def save(self, *args, **kwargs):
        commit = kwargs.get("commit", True)

        with Image.open(self.instance.source) as image:
            pil_image = MarkerGeneratorAPIView.generate_marker(
                image, inner_border=self.cleaned_data.get("inner_border", False)
            )
            blob = BytesIO()
            pil_image.save(blob, "JPEG")
            filename = self.instance.source.name
            self.instance.file_size = self.instance.source.size
            self.instance.source.save(filename, File(blob), save=commit)
            patt_str = generate_patt_from_image(image)

            self.instance.patt.save(
                f"{filename}.patt",
                ContentFile(patt_str.encode("utf-8")),
                save=commit,
            )

            if kwargs.get("owner"):
                self.instance.owner = kwargs.get("owner")
                del kwargs["owner"]

            return super(UploadMarkerForm, self).save(*args, **kwargs)


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
        artwork.scale_x = self.cleaned_data["scale"]
        artwork.scale_y = self.cleaned_data["scale"]

        if commit:
            artwork.save()
        return artwork


class ExhibitForm(forms.ModelForm):
    artworks = forms.CharField(max_length=1000, required=False)
    augmenteds = forms.CharField(max_length=1000, required=False)

    def __init__(self, *args, **kwargs):
        super(ExhibitForm, self).__init__(*args, **kwargs)
        self.fields["name"].widget.attrs["placeholder"] = _("Exhibit Title")
        self.fields["slug"].widget.attrs["placeholder"] = _(
            "Complete with your Exhibit URL here"
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
        if not re.match("^[a-zA-Z0-9_-]*$", slug):
            raise forms.ValidationError(
                _("Url can't contain spaces or special characters")
            )
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

    def clean(self):
        cleaned_data = super().clean()
        artworks = cleaned_data.get("artworks", [])
        augmenteds = cleaned_data.get("augmenteds", [])

        if not artworks and not augmenteds:
            raise forms.ValidationError(
                _("You must select at least one artwork or augmented object.")
            )

        return cleaned_data

    def save(self, commit=True):
        exhibit = super().save(commit=False)

        # Set exhibit_type based on augmented objects
        artworks = self.cleaned_data.get("artworks", [])
        augmenteds = self.cleaned_data.get("augmenteds", [])
        exhibit.exhibit_type = ExhibitTypes.MR if augmenteds else ExhibitTypes.AR

        if commit:
            exhibit.save()
            exhibit.artworks.set(artworks)
            exhibit.augmenteds.set(augmenteds)

        return exhibit


class SoundForm(forms.ModelForm):
    class Meta:
        model = Sound
        fields = ("title", "file", "author")

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if not file:
            raise forms.ValidationError(_("This field is required."))

        allowed_extensions = ["mp3", "ogg"]
        extension = getattr(file, "name", "").split(".")[-1].lower()
        if extension not in allowed_extensions:
            raise forms.ValidationError(_("Only MP3 and OGG audio files are allowed."))

        # Sound already exists, we need to check if it's being used by another user
        if self.instance.pk:
            # Compare if the file changed
            file_content = file.read()
            file.seek(0)  # Reset file pointer
            instance_content = self.instance.file.read()
            self.instance.file.seek(0)  # Reset instance file pointer

            if instance_content != file_content:
                if self.instance.is_used_by_other_user():
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
