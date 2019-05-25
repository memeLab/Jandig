from django.urls import path, re_path
from .views import service_worker, index, upload_image, exhibit_select, exhibit
from .views_s.home import home, ar_viewer, community, docs

urlpatterns = [
    re_path('^$', home, name='home'),
    #path('ar', ar_viewer, name='ar_viewer'),
    re_path('^community$', community, name='community'),
    re_path('^docs$', docs, name='docs'),
    re_path('^exhibit_select$', exhibit_select, name='exhibit_select'),
    # path('agreement', *, *),
    # path('agreement', *, *),
    re_path('sw.js', service_worker, name='sw'),
    re_path('upload', upload_image, name='upload-image'),
    re_path('.*', exhibit, name="exhibits"),
]
