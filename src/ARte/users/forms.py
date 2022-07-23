import re

from django import forms
from django.core.files.base import ContentFile, File
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm as OrigPasswordChangeForm
from django.utils.translation import gettext_lazy as _
from django.forms.widgets import HiddenInput

from .choices import COUNTRY_CHOICES
from core.models import Marker, Object

from io import BytesIO
from PIL import Image
from pymarker.core import generate_marker_from_image, generate_patt_from_image

import logging

log = logging.getLogger("ej")

User = get_user_model()


class SignupForm(UserCreationForm):
    """
    Form to register a new user
    """

    email = forms.EmailField(
        max_length=254,
        help_text=_("Your e-mail address"),
    )

    username = forms.CharField(
        max_length=12,
        help_text=_("Your username"),
    )

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)

        self.fields["email"].widget.attrs["placeholder"] = _("email")
        self.fields["username"].widget.attrs["placeholder"] = _("chosen username")
        self.fields["password1"].widget.attrs["placeholder"] = _("password")
        self.fields["password2"].widget.attrs["placeholder"] = _("confirm password")

    class Meta:
        model = User
        fields = ["email", "username", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        username = self.cleaned_data.get("username")
        if (
            email
            and User.objects.filter(email=email).exclude(username=username).exists()
        ):
            raise forms.ValidationError(_("E-mail taken"))

        return email


class PasswordChangeForm(OrigPasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields["old_password"].widget.attrs["placeholder"] = _("Old Password")
        self.fields["new_password1"].widget.attrs["placeholder"] = _("New Password")
        self.fields["new_password2"].widget.attrs["placeholder"] = _(
            "New Password Again"
        )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "bio", "country", "personal_site"]

    field_order = ["email", "username", "personal_site", "country", "bio"]

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.initial["username"] = self.instance.user.username

        # FIXME: user.email come as a string of a tuple, no idea why. "('email@bla.com',)"
        # email = self.instance.user.email.replace("('", "").replace("',)", "")
        self.initial["email"] = self.instance.user.email
        self.initial["bio"] = self.instance.bio
        self.initial["country"] = self.instance.country
        self.initial["personal_site"] = self.instance.personal_site
        self.fields["email"].widget.attrs["placeholder"] = _("E-mail")
        self.fields["username"].widget.attrs["placeholder"] = _("Username")
        self.fields["bio"].widget.attrs["placeholder"] = _("Personal Bio / Description")
        self.fields["personal_site"].widget.attrs["placeholder"] = _("Personal Website")

    email = forms.EmailField(
        max_length=254,
        help_text=_("Your e-mail address"),
    )
    username = forms.CharField(
        max_length=12,
        help_text=_("Your username"),
    )
    country = forms.ChoiceField(choices=COUNTRY_CHOICES, required=False)
    bio = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea,
        help_text=_("Personal Bio / Description"),
    )
    personal_site = forms.URLField(
        required=False,
        help_text=_("Personal Website"),
    )

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if (
            username
            and User.objects.filter(username=username)
            .exclude(username=self.instance.user.username)
            .exists()
        ):
            raise forms.ValidationError(_("Username already in use"))
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if (
            email
            and User.objects.filter(email=email)
            .exclude(username=self.instance.user.username)
            .exists()
        ):
            raise forms.ValidationError(_("Email address must be unique"))

        return email


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["placeholder"] = _("username / email")
        self.fields["password"].widget.attrs["placeholder"] = _("password")

    def clean_username(self):
        username_or_email = self.cleaned_data.get("username")
        if "@" in username_or_email:
            if not User.objects.filter(email=username_or_email).exists():
                raise forms.ValidationError(_("Username/email not found"))
            user = User.objects.get(email=username_or_email)
            if user:
                return user.username
        else:
            if not User.objects.filter(username=username_or_email).exists():
                raise forms.ValidationError(_("Username/email not found"))

        # Already is a valid username
        return username_or_email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        username_or_email = self.data.get("username")
        user = None
        username_or_email_wrong = False

        if "@" in username_or_email:
            if User.objects.filter(email=username_or_email).exists():
                username = User.objects.get(email=username_or_email).username
                user = authenticate(username=username, password=password)
            else:
                username_or_email_wrong = True
                # raise forms.ValidationError(_('Email Wrong!'))
        else:
            if User.objects.filter(username=username_or_email).exists():
                user = authenticate(username=username_or_email, password=password)
            else:
                username_or_email_wrong = True
                # raise forms.ValidationError(_('Username Wrong!'))

        if not user and not username_or_email_wrong:
            raise forms.ValidationError(_("Wrong password!"))

        return password


class RecoverPasswordForm(forms.Form):
    username_or_email = forms.CharField(label="username / email", max_length="50")


class RecoverPasswordCodeForm(forms.Form):
    verification_code = forms.CharField(label="Verification code", max_length="200")


class UploadMarkerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UploadMarkerForm, self).__init__(*args, **kwargs)

        log.warning(self.fields)
        self.fields["source"].widget.attrs["placeholder"] = _("browse file")
        self.fields["source"].widget.attrs["accept"] = "image/png, image/jpg"
        self.fields["author"].widget.attrs["placeholder"] = _(
            "declare different author name"
        )
        self.fields["title"].widget.attrs["placeholder"] = _("Marker's title")

    class Meta:
        model = Marker
        exclude = ("owner", "uploaded_at", "patt")

    def save(self, *args, **kwargs):
        with Image.open(self.instance.source) as image:
            pil_image = generate_marker_from_image(image)
            blob = BytesIO()
            pil_image.save(blob, "JPEG")
            filename = self.instance.source.name
            self.instance.source.save(filename, File(blob), save=False)
            patt_str = generate_patt_from_image(image)
            self.instance.patt.save(
                filename + ".patt", ContentFile(patt_str.encode("utf-8")), save=False
            )

            if kwargs.get("owner"):
                self.instance.owner = kwargs.get("owner")
                del kwargs["owner"]
            self.instance.save()

            return super(UploadMarkerForm, self).save(*args, **kwargs)


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
        log.warning(self.fields)

    class Meta:
        model = Object
        fields = ("source", "author", "title", "scale", "position", "rotation")


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
            "declare different author name"
        )
        self.fields["augmented_author"].widget.attrs["placeholder"] = _(
            "declare different author name"
        )
        self.fields["title"].widget.attrs["placeholder"] = _("Artwork title")
        self.fields["description"].widget.attrs["placeholder"] = _(
            "Artwork description"
        )


class ExhibitForm(forms.Form):

    name = forms.CharField(max_length=50, required=True)
    slug = forms.CharField(max_length=50, required=True)

    # FIXME: maybe this can be improved. Possible bug on max artworks per exhibit
    artworks = forms.CharField(max_length=1000)

    def clean_slug(self):
        data = self.cleaned_data["slug"]
        if not re.match("^[a-zA-Z0-9_]*$", data):
            raise forms.ValidationError(
                _("Url can't contain spaces or special characters")
            )
        return data

    def __init__(self, *args, **kwargs):
        super(ExhibitForm, self).__init__(*args, **kwargs)

        self.fields["name"].widget.attrs["placeholder"] = _("Exhibit Title")
        self.fields["slug"].widget.attrs["placeholder"] = _(
            "Complete with your Exhibit URL here"
        )
