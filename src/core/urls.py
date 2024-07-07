from django.conf import settings
from django.urls import include, path
from rest_framework_nested.routers import DefaultRouter

from core.views.artworks import ArtworkViewset
from core.views.exhibits import ExhibitViewset
from core.views.markers import MarkerViewset
from core.views.objects import ObjectViewset
from core.views.static_views import (
    community,
    documentation,
    health_check,
    home,
    marker_generator,
)
from core.views.views import (
    artwork_preview,
    collection,
    exhibit_detail,
    exhibit_select,
    manifest,
    robots_txt,
    see_all,
    service_worker,
    upload_image,
)

api_router = DefaultRouter()
api_router.register("markers", MarkerViewset, basename="marker")
api_router.register("objects", ObjectViewset, basename="object")
api_router.register("artworks", ArtworkViewset, basename="artwork")
api_router.register("exhibits", ExhibitViewset, basename="exhibit")

urlpatterns = [
    path("", home, name="home"),
    path("api/v1/", include(api_router.urls)),
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
    path("see_all/", see_all, name="see_all"),
    path("robots.txt/", robots_txt),
    path(settings.HEALTH_CHECK_URL, health_check),
]
