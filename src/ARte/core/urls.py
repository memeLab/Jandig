from django.urls import path, re_path, include
from .views import service_worker, index, upload_image, exhibit_select, collection, exhibit_detail, lang_selector
from .views_s.home import home, ar_viewer, community, marker_generator

urlpatterns = [
    path('', home, name='home'),
    #path('ar', ar_viewer, name='ar_viewer'),
    path('community/', community, name='community'),
    path('collection/', collection, name='collection'),
    path('exhibit_select/', exhibit_select, name='exhibit_select'),
    path('exhibit/', exhibit_detail, name="exhibit-detail"),
    path('generator/', marker_generator, name='marker-generator'),
    path('sw.js', service_worker, name='sw'),
    path('upload', upload_image, name='upload-image'),
    path('i18n/', include('django.conf.urls.i18n')),
]
