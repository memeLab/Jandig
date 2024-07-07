import debug_toolbar
from django.conf import settings
from django.conf.urls.static import serve
from django.contrib import admin
from django.urls import include, path, re_path

urlpatterns = [
    path(settings.DJANGO_ADMIN_URL, admin.site.urls),
    path("users/", include("users.urls")),
    path("memories/", include("blog.urls")),
    re_path("^docs/(?P<path>.*)$", serve, {"document_root": settings.DOCS_ROOT}),
    path("", include("core.urls")),
    path("", include("core.routes")),
]

urlpatterns += [
    path("__debug__/", include(debug_toolbar.urls)),
]
