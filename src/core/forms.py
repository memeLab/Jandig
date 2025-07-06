import re

from django import forms
from django.forms.widgets import HiddenInput, NumberInput
from django.utils.translation import gettext_lazy as _

from .models import Exhibit, Object


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
            return file
        allowed_mimetypes = ["image/gif", "video/mp4", "video/webm"]
        allowed_extensions = [".gif", ".mp4", ".webm"]
        content_type = getattr(file, "content_type", None)
        name = getattr(file, "name", "").lower()
        if content_type not in allowed_mimetypes or not any(
            name.endswith(ext) for ext in allowed_extensions
        ):
            raise forms.ValidationError(
                _("Only GIF images, MP4, and WebM videos are allowed.")
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
