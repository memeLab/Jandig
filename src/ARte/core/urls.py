from django.urls import path
from .views import service_worker, index, upload_image
from .views_s.home import home


urlpatterns = [
    path('sw.js', service_worker, name='sw'),
    path('upload', upload_image, name='upload-image'),
    path('', home, name='home'),
]
