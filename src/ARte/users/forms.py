from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

class SignupForm(UserCreationForm):
    """
    Form to register a new user
    """

    # first_name = forms.CharField(
    #     max_length=30,
    #     required=True,
    #     help_text='Your first name',

    # )
    # last_name = forms.CharField(
    #     max_length=30,
    #     required=True,
    #     help_text='Your last name'
    # )
    email = forms.EmailField(
        max_length=254,
        help_text='Your e-mail address',
    )

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        
        self.fields['email'].widget.attrs['placeholder'] = 'email'
        self.fields['username'].widget.attrs['placeholder'] = 'chosen username'
        self.fields['password1'].widget.attrs['placeholder'] = 'password'
        self.fields['password2'].widget.attrs['placeholder'] = 'confirm password'

    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2']
