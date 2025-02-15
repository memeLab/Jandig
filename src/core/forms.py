from django import forms
from django.utils.safestring import mark_safe

from .models import Exhibit



class ListTextWidget(forms.TextInput):
    def __init__(self, *args, **kwargs):
        super(ListTextWidget, self).__init__(*args, **kwargs)
        self._name = "exhibit-list"
        self._list = Exhibit.objects.all().order_by("name")
        self.attrs.update({"list": f"list__{self._name}"})

    def render(self, name, value, attrs=None, renderer=None):
        text_html = super(ListTextWidget, self).render(name, value, attrs=attrs)
        data_list = f'<datalist id="list__{self._name}">'
        for item in self._list:
            data_list += f'<option value="{item.slug}">{item.name}</option>'
        data_list += "</datalist>"
        return mark_safe(text_html + data_list)


class ExhibitForm(forms.Form):
    exhibit = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super(ExhibitForm, self).__init__(*args, **kwargs)
        self.fields["exhibit"].widget = ListTextWidget()
        self.fields["exhibit"].label = ""
