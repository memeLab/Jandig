import re
from io import BytesIO

from django import forms
from django.core.files.base import ContentFile, File
from django.forms.widgets import HiddenInput, NumberInput
from django.template import loader
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from PIL import Image
from pymarker.core import generate_patt_from_image

from core.models import Marker
from core.views.api_views import MarkerGeneratorAPIView

from .models import Exhibit, Object

DEFAULT_AUTHOR_PLACEHOLDER = "declare different author name"


class RangeInput(NumberInput):
    input_type = "range"


class ExhibitSelectForm(forms.Form):
    exhibit = forms.ModelChoiceField(queryset=Exhibit.objects.all().order_by("name"))


class ExhibitForm(forms.Form):
    name = forms.CharField(max_length=50, required=True)
    slug = forms.CharField(max_length=50, required=True)

    artworks = forms.CharField(max_length=1000)

    def __init__(self, *args, **kwargs):
        self.exhibit_id = kwargs.pop("exhibit_id", None)
        super(ExhibitForm, self).__init__(*args, **kwargs)
        self.fields["name"].widget.attrs["placeholder"] = _("Exhibit Title")
        self.fields["slug"].widget.attrs["placeholder"] = _(
            "Complete with your Exhibit URL here"
        )

    def clean_name(self):
        name = self.cleaned_data["name"]
        qs = Exhibit.objects.filter(name=name)
        if self.exhibit_id:
            qs = qs.exclude(id=self.exhibit_id)
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
        if self.exhibit_id:
            qs = qs.exclude(id=self.exhibit_id)
        if qs.exists():
            raise forms.ValidationError(
                _(
                    "That exhibit slug is already in use. Please choose another slug for your exhibit."
                )
            )
        return slug


class ObjectWidget(forms.ClearableFileInput):
    """Custom widget for displaying an object correctly on edit forms if it is an image or video."""

    template_name = "core/templates/object_edit_template.jinja2"

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)


class UploadObjectForm(forms.ModelForm):
    scale = forms.FloatField(
        min_value=0.1,
        max_value=5.0,
        required=True,
        label=_("Scale (0.1 to 5.0)"),
        help_text=_(
            "Enter a value from 0.1 (reduce object to 10%% its size) to 5.0 (increase object to 500%% its size)"
        ),
        initial=1.0,
        widget=RangeInput,
    )

    def __init__(self, *args, **kwargs):
        super(UploadObjectForm, self).__init__(*args, **kwargs)

        self.fields["source"].widget = ObjectWidget()
        self.fields["source"].widget.attrs["placeholder"] = _("browse file")
        self.fields["source"].widget.attrs["accept"] = "image/gif, .gif, .mp4, .webm"
        self.fields["author"].widget.attrs["placeholder"] = _(
            "declare different author name"
        )
        self.fields["position"].widget = HiddenInput()
        self.fields["title"].widget.attrs["placeholder"] = _("Object's title")
        self.fields["scale"].widget.attrs["placeholder"] = _("0.1 ~ 5.0")
        self.fields["scale"].widget.attrs["step"] = 0.1
        self.fields["scale"].widget.attrs["class"] = "slider"

    class Meta:
        model = Object
        fields = ("source", "author", "title", "scale", "position")

    def clean_source(self):
        file = self.cleaned_data.get("source")
        if not file:
            raise forms.ValidationError(_("This field is required."))

        allowed_extensions = ["gif", "mp4", "webm"]
        extension = getattr(file, "name", "").split(".")[-1].lower()
        if extension not in allowed_extensions:
            raise forms.ValidationError(
                _("Only GIF images, MP4, and WebM videos are allowed.")
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

    def clean_scale(self):
        scale_val = self.cleaned_data["scale"]
        if not (0.1 <= scale_val <= 5.0):
            raise forms.ValidationError(_("Scale must be between 0.1 and 5.0"))
        # Convert to string for saving
        return f"{scale_val:.2f} {scale_val:.2f}"

    def save(self, *args, **kwargs):
        if owner := kwargs.get("owner", None):
            self.instance.owner = owner
            del kwargs["owner"]

        self.instance.file_size = self.instance.source.size

        return super(UploadObjectForm, self).save(*args, **kwargs)


class UploadMarkerForm(forms.ModelForm):
    inner_border = forms.BooleanField(
        required=False,
        label=_("Add inner border"),
    )

    def __init__(self, *args, **kwargs):
        super(UploadMarkerForm, self).__init__(*args, **kwargs)

        self.fields["source"].widget.attrs["placeholder"] = _("browse file")
        self.fields["source"].widget.attrs["accept"] = "image/png, image/jpg"
        self.fields["author"].widget.attrs["placeholder"] = _(
            DEFAULT_AUTHOR_PLACEHOLDER
        )
        self.fields["title"].widget.attrs["placeholder"] = _("Marker's title")

    class Meta:
        model = Marker
        exclude = ("owner", "created", "patt", "file_size")

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


class ArtworkForm(forms.Form):
    marker = forms.ImageField(required=False)
    marker_author = forms.CharField(max_length=12, required=False)
    augmented = forms.ImageField(required=False)
    augmented_author = forms.CharField(max_length=12, required=False)
    existent_marker = forms.IntegerField(min_value=1, required=False)
    existent_object = forms.IntegerField(min_value=1, required=False)
    title = forms.CharField(max_length=50)
    description = forms.CharField(widget=forms.Textarea, max_length=500, required=False)

    def __init__(self, *args, **kwargs):
        super(ArtworkForm, self).__init__(*args, **kwargs)

        self.fields["marker_author"].widget.attrs["placeholder"] = _(
            DEFAULT_AUTHOR_PLACEHOLDER
        )
        self.fields["augmented_author"].widget.attrs["placeholder"] = _(
            DEFAULT_AUTHOR_PLACEHOLDER
        )
        self.fields["title"].widget.attrs["placeholder"] = _("Artwork title")
        self.fields["description"].widget.attrs["placeholder"] = _(
            "Artwork description"
        )
