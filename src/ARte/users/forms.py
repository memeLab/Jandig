from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

class SignupForm(UserCreationForm):
    """
    Form to register a new user
    """
    first_name = forms.CharField(
        max_length=30,
        required=True,
        help_text='Your first name'
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        help_text='Your last name'
    )
    email = forms.EmailField(
        max_length=254,
        help_text='Your e-mail address'
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
