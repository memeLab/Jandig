from django.urls import path
from .views import service_worker, index, upload_image, marker_generator


urlpatterns = [
    path('sw.js', service_worker, name='sw'),
    path('upload', upload_image, name='upload-image'),
    path('generator', marker_generator, name='marker-generator'),
    path('', index, name='index'),
]
