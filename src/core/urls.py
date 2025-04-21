from django.conf import settings
from django.urls import include, path, re_path

from core.views.static_views import (
    community,
    documentation,
    favicon,
    health_check,
    home,
    marker_generator,
    robots_txt,
)
from core.views.views import (
    artwork_preview,
    collection,
    create_exhibit,
    edit_exhibit,
    edit_object,
    exhibit,
    exhibit_detail,
    exhibit_select,
    manifest,
    object_upload,
    related_content,
    see_all,
    service_worker,
)

urlpatterns = [
    path("", home, name="home"),
    path("documentation/", documentation, name="documentation"),
    path("community/", community, name="community"),
    path("collection/", collection, name="collection"),
    path("exhibit_select/", exhibit_select, name="exhibit_select"),
    path("exhibit/", exhibit_detail, name="exhibit-detail"),
    path("exhibits/create/", create_exhibit, name="create-exhibit"),
    path("exhibits/edit/", edit_exhibit, name="edit-exhibit"),
    path("artwork/", artwork_preview, name="artwork-preview"),
    path("objects/upload/", object_upload, name="object-upload"),
    path("objects/edit/", edit_object, name="edit-object"),
    path("generator/", marker_generator, name="marker-generator"),
    path("related-content", related_content, name="related-content"),
    path("sw.js", service_worker, name="sw"),
    path("manifest.json", manifest, name="manifest"),
    path("i18n/", include("django.conf.urls.i18n")),
    re_path(
        r"^see_all(?:/(?P<which>[a-zA-Z]+))?(?:/(?P<page>\d+))?/$",
        see_all,
        name="see_all",
    ),
    path("robots.txt", robots_txt),
    path("favicon.ico", favicon),
    path(settings.HEALTH_CHECK_URL, health_check),
    path("<slug:slug>/", exhibit, name="exhibit"),
]
