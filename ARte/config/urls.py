from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from .wait_db import start_services

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pwa.urls')),
]

start_services(settings)