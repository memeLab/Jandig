import re

from django import forms
from django.forms.widgets import HiddenInput
from django.utils.translation import gettext_lazy as _

from .models import Exhibit, Object


class ExhibitSelectForm(forms.Form):
    exhibit = forms.ModelChoiceField(queryset=Exhibit.objects.all().order_by("name"))


class ExhibitForm(forms.Form):
    name = forms.CharField(max_length=50, required=True)
    slug = forms.CharField(max_length=50, required=True)

    # FIXME: maybe this can be improved. Possible bug on max artworks per exhibit
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
    def __init__(self, *args, **kwargs):
        super(UploadObjectForm, self).__init__(*args, **kwargs)

        self.fields["source"].widget.attrs["placeholder"] = _("browse file")
        self.fields["source"].widget.attrs["accept"] = "image/*, .mp4, .webm"
        self.fields["author"].widget.attrs["placeholder"] = _(
            "declare different author name"
        )
        self.fields["scale"].widget = HiddenInput()
        self.fields["rotation"].widget = HiddenInput()
        self.fields["position"].widget = HiddenInput()
        self.fields["title"].widget.attrs["placeholder"] = _("Object's title")

    class Meta:
        model = Object
        fields = ("source", "author", "title", "scale", "position", "rotation")

    def save(self, *args, **kwargs):
        if owner := kwargs.get("owner", None):
            self.instance.owner = owner
            del kwargs["owner"]

        self.instance.file_size = self.instance.source.size

        return super(UploadObjectForm, self).save(*args, **kwargs)
