import debug_toolbar
from django.conf import settings
from django.conf.urls.static import serve
from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework_nested.routers import DefaultRouter

from core.views.viewsets import (
    ArtworkViewset,
    ExhibitViewset,
    MarkerViewset,
    ObjectViewset,
)
api_router = DefaultRouter()
api_router.register("markers", MarkerViewset, basename="marker")
api_router.register("objects", ObjectViewset, basename="object")
api_router.register("artworks", ArtworkViewset, basename="artwork")
api_router.register("exhibits", ExhibitViewset, basename="exhibit")

urlpatterns = [
    path(settings.DJANGO_ADMIN_URL, admin.site.urls),
    path("api/v1/", include(api_router.urls)),
    path("users/", include("users.urls")),
    path("memories/", include("blog.urls")),
    re_path("^docs/(?P<path>.*)$", serve, {"document_root": settings.DOCS_ROOT}),
    path("", include("core.urls")),
]

urlpatterns += [
    path("__debug__/", include(debug_toolbar.urls)),
]
