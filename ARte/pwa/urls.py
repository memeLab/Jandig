from django.urls import path
from .views import service_worker, index


urlpatterns = [
    path('sw.js', service_worker, name='sw'),
    path('', index, name='index'),
]
