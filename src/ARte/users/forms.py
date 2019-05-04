from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class SignupForm(forms.ModelForm):
    """
    Form to register a new user
    """
    password = forms.CharField(
        label='Password',
        required=True,
        widget=forms.PasswordInput,
        help_text='Your password'
    )
    password_confirm = forms.CharField(
        label='Password confirmation',
        required=True,
        widget=forms.PasswordInput,
        help_text='Confirm your password'
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']

    def _post_clean(self):
        super()._post_clean()
        data = self.cleaned_data
        if data.get('password') != data.get('password_confirm'):
            self.add_error('password_confirm', 'Passwords do not match')