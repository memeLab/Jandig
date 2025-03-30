from django import forms

from .models import Exhibit


class ExhibitForm(forms.Form):
    exhibit = forms.ModelChoiceField(queryset=Exhibit.objects.all().order_by("name"))
