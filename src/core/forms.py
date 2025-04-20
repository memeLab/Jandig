import re

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Exhibit


class ExhibitSelectForm(forms.Form):
    exhibit = forms.ModelChoiceField(queryset=Exhibit.objects.all().order_by("name"))


class ExhibitForm(forms.Form):
    name = forms.CharField(max_length=50, required=True)
    slug = forms.CharField(max_length=50, required=True)

    # FIXME: maybe this can be improved. Possible bug on max artworks per exhibit
    artworks = forms.CharField(max_length=1000)

    def clean_name(self):
        name = self.cleaned_data["name"]
        if Exhibit.objects.filter(name=name).exists():
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
        if Exhibit.objects.filter(slug=slug).exists():
            raise forms.ValidationError(
                _(
                    "That exhibit slug is already in use. Please choose another slug for your exhibit."
                )
            )
        return slug

    def __init__(self, *args, **kwargs):
        super(ExhibitForm, self).__init__(*args, **kwargs)

        self.fields["name"].widget.attrs["placeholder"] = _("Exhibit Title")
        self.fields["slug"].widget.attrs["placeholder"] = _(
            "Complete with your Exhibit URL here"
        )
