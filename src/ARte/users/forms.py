from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import ugettext_lazy as _

from .models import Marker, Object, Artwork

User = get_user_model()

class SignupForm(UserCreationForm):
    """
    Form to register a new user
    """

    email = forms.EmailField(
        max_length=254,
        help_text=_('Your e-mail address'),
    )

    username = forms.CharField(
        max_length=12,
        help_text=_('Your username'),
    )

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        
        self.fields['email'].widget.attrs['placeholder'] = _('email')
        self.fields['username'].widget.attrs['placeholder'] = _('chosen username')
        self.fields['password1'].widget.attrs['placeholder'] = _('password')
        self.fields['password2'].widget.attrs['placeholder'] = _('confirm password')

    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError(_('Email address must be unique'))

        return email


class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['placeholder'] = _('username / email')
        self.fields['password'].widget.attrs['placeholder'] = _('password')

    def clean_username(self):
        username_or_email = self.cleaned_data.get('username')
        if '@' in username_or_email:
            user = User.objects.get(email=username_or_email)
            if user:
                return user.username

        return username_or_email


class UploadMarkerForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(UploadMarkerForm, self).__init__(*args, **kwargs)

        self.fields['source'].widget.attrs['placeholder'] = _('browse file')
        self.fields['patt'].widget.attrs['placeholder'] = _('browse file')
        self.fields['author'].widget.attrs['placeholder'] = _('declare different author name')
    
    class Meta:
        model = Marker
        exclude = ('owner',)


class UploadObjectForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(UploadObjectForm, self).__init__(*args, **kwargs)

        self.fields['source'].widget.attrs['placeholder'] = _('browse file')
        self.fields['author'].widget.attrs['placeholder'] = _('declare different author name')
    
    class Meta:
        model = Object
        exclude = ('owner','scale','rotation','position')


class ArtworkForm(forms.Form):

    marker = forms.ImageField(required=False)
    marker_author = forms.CharField(max_length=12, required=False)
    augmented = forms.ImageField(required=False)
    augmented_author = forms.CharField(max_length=12, required=False)
    existent_marker = forms.IntegerField(min_value=1, required=False)
    existent_object = forms.IntegerField(min_value=1, required=False)
    title = forms.CharField(max_length=50)
    description = forms.CharField(widget=forms.Textarea, max_length=500)

    def __init__(self, *args, **kwargs):
        super(ArtworkForm, self).__init__(*args, **kwargs)

        self.fields['marker_author'].widget.attrs['placeholder'] = _('declare different author name')
        self.fields['augmented_author'].widget.attrs['placeholder'] = _('declare different author name')
        self.fields['title'].widget.attrs['placeholder'] = _('artwork title')
        self.fields['description'].widget.attrs['placeholder'] = _('artwork description')


class ExhibitForm(forms.Form):

    name = forms.CharField(max_length=12, required=True)
    slug = forms.CharField(max_length=12, required=True)

    # FIXME: maybe this can be improved. Possible bug on max artworks per exhibit 
    artworks = forms.CharField(max_length=1000)

    def __init__(self, *args, **kwargs):
        super(ExhibitForm, self).__init__(*args, **kwargs)

        self.fields['name'].widget.attrs['placeholder'] = _('Exhibit Title')
        self.fields['slug'].widget.attrs['placeholder'] = _('Exhibit URL')
