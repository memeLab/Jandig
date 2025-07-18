from django.contrib.auth import views as auth_views
from django.urls import path

from .forms import LoginForm
from .views import (
    ResetPasswordView,
    edit_password,
    edit_profile,
    profile,
    signup,
)

urlpatterns = [
    path("signup/", signup, name="signup"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="users/login.jinja2",
            authentication_form=LoginForm,
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/reset-password/password_reset_confirm.jinja2"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/reset-password/password_reset_complete.jinja2"
        ),
        name="password_reset_complete",
    ),
    path("profile/", profile, name="profile"),
    path("profile/edit/", edit_profile, name="edit-profile"),
    path("profile/edit-password/", edit_password, name="edit-password"),
]
