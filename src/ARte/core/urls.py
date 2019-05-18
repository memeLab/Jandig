from django.urls import path
from .views import service_worker, index, upload_image
from .views_s.home import home, ar_viewer, community, docs


urlpatterns = [
    path('', home, name='home'),
    path('ar', ar_viewer, name='ar_viewer'),
    path('community', community, name='community'),
    path('docs', docs, name='docs'),
    # path('agreement', *, *),
    # path('agreement', *, *),

    path('sw.js', service_worker, name='sw'),
    path('upload', upload_image, name='upload-image'),
]
