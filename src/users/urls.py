from django.contrib.auth import views as auth_views
from django.urls import path

from .forms import LoginForm
from .views import (
    ResetPasswordView,
    create_artwork,
    create_exhibit,
    delete,
    edit_artwork,
    edit_exhibit,
    edit_marker,
    edit_object,
    edit_password,
    edit_profile,
    marker_upload,
    mod,
    mod_delete,
    object_upload,
    permission_denied,
    profile,
    related_content,
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
    path("markers/upload/", marker_upload, name="marker-upload"),
    path("objects/upload/", object_upload, name="object-upload"),
    path("objects/edit/", edit_object, name="edit-object"),
    path("markers/edit/", edit_marker, name="edit-marker"),
    path("artworks/create/", create_artwork, name="create-artwork"),
    path("artworks/edit/", edit_artwork, name="edit-artwork"),
    path("exhibits/create/", create_exhibit, name="create-exhibit"),
    path("exhibits/edit/", edit_exhibit, name="edit-exhibit"),
    path("content/delete/", delete, name="delete-content"),
    path("moderator-page/", mod, name="moderator-page"),
    path("permission-denied/", permission_denied, name="permission-denied"),
    path("content/mod-delete/", mod_delete, name="mod-delete-content"),
    path("related-content", related_content, name="related-content"),
]
