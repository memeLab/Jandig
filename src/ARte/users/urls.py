from django.urls import path
from django.contrib.auth import views as auth_views

from .forms import LoginForm
from .views import signup, profile, marker_upload, object_upload, create_artwork, create_exhibit, edit_artwork, element_get, edit_exhibit, edit_profile, edit_password

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(
        template_name='users/login.jinja2',
        authentication_form=LoginForm,
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('recover/', auth_views.PasswordResetView.as_view(), name='recover'),

    path('profile/', profile, name='profile'),
    path('profile/edit/', edit_profile, name="edit-profile"),
    path('profile/edit-password/', edit_password, name="edit-password"),
    ## deal with password reset

    path('markers/upload/', marker_upload, name='marker-upload'),
    path('objects/upload/', object_upload, name='object-upload'),
    path('element/get/', element_get, name='element-get'),

    path('artworks/create/', create_artwork, name='create-artwork'),
    path('artworks/edit/', edit_artwork, name="edit-artwork"),
    
    path('exhibits/create/', create_exhibit, name='create-exhibit'),
    path('exhibits/edit/', edit_exhibit, name='edit-exhibit'),
]
