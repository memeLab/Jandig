from django.urls import path, include
from .views import (
    artwork_preview,
    see_all,
    service_worker,
    upload_image,
    exhibit_select,
    collection,
    exhibit_detail,
    manifest,
    robots_txt,
)
from .views_s.home import home, community, marker_generator, documentation, health_check

urlpatterns = [
    path("", home, name="home"),
    path("documentation/", documentation, name="documentation"),
    path("community/", community, name="community"),
    path("collection/", collection, name="collection"),
    path("exhibit_select/", exhibit_select, name="exhibit_select"),
    path("exhibit/", exhibit_detail, name="exhibit-detail"),
    path("artwork/", artwork_preview, name="artwork-preview"),
    path("generator/", marker_generator, name="marker-generator"),
    path("sw.js", service_worker, name="sw"),
    path("manifest.json", manifest, name="manifest"),
    path("upload", upload_image, name="upload-image"),
    path("i18n/", include("django.conf.urls.i18n")),
    path("see_all/", see_all, name="see-all"),
    path("robots.txt/", robots_txt),
    path("status/", health_check),
]
