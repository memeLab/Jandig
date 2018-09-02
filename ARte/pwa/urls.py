from django.urls import path
from django.contrib.auth import views as auth_views
from .views import index

urlpatterns = [
    path('', index, name='index'),
]