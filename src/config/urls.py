import os

import debug_toolbar
from django.conf import settings
from django.conf.urls.static import serve, static
from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework_nested.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from core.views.viewsets import (
    ArtworkViewset,
    ExhibitViewset,
    MarkerViewset,
    ObjectViewset,
)
from users.viewsets import ProfileViewset

api_router = DefaultRouter()
api_router.register("markers", MarkerViewset, basename="marker")
api_router.register("objects", ObjectViewset, basename="object")
api_router.register("artworks", ArtworkViewset, basename="artwork")
api_router.register("exhibits", ExhibitViewset, basename="exhibit")
api_router.register("profiles", ProfileViewset, basename="profile")

urlpatterns = [
    path(settings.DJANGO_ADMIN_URL, admin.site.urls),
    path("api/v1/", include(api_router.urls)),
    path("api/v1/auth/login/", TokenObtainPairView.as_view(), name="login"),
    path("api/v1/auth/verify/", TokenVerifyView.as_view(), name="verify"),
    path("api/v1/auth/refresh/", TokenRefreshView().as_view(), name="refresh"),
    path("users/", include("users.urls")),
    path("memories/", include("blog.urls")),
    re_path("^docs/(?P<path>.*)$", serve, {"document_root": settings.DOCS_ROOT}),
    path("", include("core.urls")),
]

if not settings.USE_GUNICORN:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path("__debug__/", include(debug_toolbar.urls)),
]

if os.getenv("USE_GUNICORN", "true").lower() in ("false", "0"):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
