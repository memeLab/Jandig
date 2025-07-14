import logging

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm as OrigPasswordChangeForm
from django.utils.translation import gettext_lazy as _

from .choices import COUNTRY_CHOICES

log = logging.getLogger(__file__)

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
