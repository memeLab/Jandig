import logging
import re
from io import BytesIO

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm as OrigPasswordChangeForm
from django.contrib.auth.forms import UserCreationForm
from django.core.files.base import ContentFile, File
from django.forms.widgets import HiddenInput
from django.utils.translation import gettext_lazy as _
from PIL import Image
from pymarker.core import generate_marker_from_image, generate_patt_from_image

from core.models import Marker, Object, Exhibit

from .choices import COUNTRY_CHOICES

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
        assume_scheme=True,
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

    def clean(self):
        username_or_email = self.cleaned_data.get("username", "")
        search_by = {}

        if "@" in username_or_email:
            search_by["email"] = username_or_email
        else:
            search_by["username"] = username_or_email

        try:
            user = User.objects.get(**search_by)
        except User.DoesNotExist as e:
            raise forms.ValidationError(_("Username/email not found")) from e

        self.cleaned_data["username"] = user.username

        password = self.cleaned_data.get("password")

        logged_user = authenticate(
            self.request, username=user.username, password=password
        )
        if logged_user is None:
            raise forms.ValidationError(_("Wrong password!"))

        self.user = logged_user

        return self.cleaned_data

    def get_user(self):
        return getattr(self, "user", None)


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
        commit = kwargs.get("commit", True)

        with Image.open(self.instance.source) as image:
            pil_image = generate_marker_from_image(image)
            blob = BytesIO()
            pil_image.save(blob, "JPEG")
            filename = self.instance.source.name
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

    def save(self, *args, **kwargs):
        if owner := kwargs.get("owner", None):
            self.instance.owner = owner
            del kwargs["owner"]

        return super(UploadObjectForm, self).save(*args, **kwargs)


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

    def clean_name(self):
        name = self.cleaned_data["name"]
        if Exhibit.objects.filter(slug=name).exists():
            raise forms.ValidationError(
                _("This name is already being used. Please choose another name for your exhibit."))
        return name

    def clean_slug(self):
        slug = self.cleaned_data["slug"]
        if not re.match("^[a-zA-Z0-9_]*$", slug):
            raise forms.ValidationError(_("Url can't contain spaces or special characters"))
        if Exhibit.objects.filter(slug=slug).exists():
            raise forms.ValidationError(
                _("That exhibit slug is already in use. Please choose another slug for your exhibit."))
        return slug

    def __init__(self, *args, **kwargs):
        super(ExhibitForm, self).__init__(*args, **kwargs)

        self.fields["name"].widget.attrs["placeholder"] = _("Exhibit Title")
        self.fields["slug"].widget.attrs["placeholder"] = _(
            "Complete with your Exhibit URL here"
        )
