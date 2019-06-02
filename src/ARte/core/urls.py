from django.urls import path, re_path
from .views import service_worker, index, upload_image, exhibit_select
from .views_s.home import home, ar_viewer, community, docs, marker_generator

urlpatterns = [
    path('', home, name='home'),
    #path('ar', ar_viewer, name='ar_viewer'),
    path('community/', community, name='community'),
    path('docs/', docs, name='docs'),
    path('exhibit_select/', exhibit_select, name='exhibit_select'),
    path('generator', marker_generator, name='marker-generator'),
    # path('agreement', *, *),
    # path('agreement', *, *),
    path('sw.js', service_worker, name='sw'),
    path('upload', upload_image, name='upload-image'),
]
