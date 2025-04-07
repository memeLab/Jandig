from django.contrib import admin

from django.urls import reverse
from django.db.models import Count
from core.models import Artwork, Exhibit, Marker, Object

from django.utils.html import format_html

def create_link_to_related_artworks(obj, artworks_list):
    """Link to related Artworks"""
    if obj.artworks_count == 0:
        return obj._artworks_count
    artworks_list = ",".join([str(artwork.id) for artwork in artworks_list])

    link = reverse("admin:index") + "core/artwork/?id__in=" + str(artworks_list)
    return format_html('<a href="{}">{}</a>', link, obj._artworks_count)

def format_marker_as_html(obj):
    return format_html(
            '<img src="{}" style="height:200px; width:200px;"/>', obj.source.url
        )

def format_object_as_html(obj):
    """Image preview with proportions"""
    max_height = 200
    max_width = 200
    height = max_height * obj.yproportion
    width = max_width * obj.xproportion
    if obj.is_video:
        return format_html(
            '<video width="{}" height="{}" controls><source src="{}" type="video/mp4"></video>',
            width,
            height,
            obj.source.url,
        )
    return format_html(
        '<img src="{}" style="height:{}px; width:{}px;"/>',
        obj.source.url,
        height,
        width,
    )


class BaseMarkerObjectAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "image_preview",
        "id",
        "owner",
        "author",
        "artworks_count",
        "exhibits_count",
        "uploaded_at",
        "filesize",
    ]
    search_fields = ["title", "id"]
    ordering = ["-uploaded_at"]

    def get_queryset(self, request):
        queryset = (
            super()
            .get_queryset(request)
            .select_related("owner")
            .prefetch_related("artworks", "artworks__exhibits")
        )
        queryset = queryset.annotate(
            _artworks_count=Count("artworks", distinct=True),
            _exhibits_count=Count("artworks__exhibits", distinct=True),
        )
        return queryset

    def artworks_count(self, obj):
        return create_link_to_related_artworks(obj, obj.artworks.all())
    artworks_count.short_description = "Artworks Count"
    artworks_count.allow_tags = True
    
    def exhibits_count(self, obj):
        return obj._exhibits_count

    def filesize(self, obj):
        """File size in MB"""
        if obj.file_size > 0:
            return f"{obj.file_size / 1024 / 1024:.2f} MB"
        return obj.file_size

    filesize.short_description = "File Size"
    filesize.admin_order_field = "file_size"
    artworks_count.admin_order_field = "_artworks_count"
    exhibits_count.admin_order_field = "_exhibits_count"


@admin.register(Marker)
class MarkerAdmin(BaseMarkerObjectAdmin):
    def image_preview(self, obj):
        return format_marker_as_html(obj)


@admin.register(Object)
class ObjectAdmin(BaseMarkerObjectAdmin):
    def image_preview(self, obj):
        return format_object_as_html(obj)

@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "id",
        "author",
        "marker_preview",
        "augmented_preview",
        "exhibits_count",
        "created_at",
    ]
    search_fields = ["title", "id"]
    ordering = ["-created_at"]

    def get_queryset(self, request):
        queryset = (
            super()
            .get_queryset(request)
            .select_related("author", "marker", "augmented")
            .prefetch_related("exhibits")
        )
        queryset = queryset.annotate(
            _exhibits_count=Count("exhibits", distinct=True),
        )
        return queryset

    def exhibits_count(self, obj):
        return obj._exhibits_count
    
    exhibits_count.admin_order_field = "_exhibits_count"
    exhibits_count.short_description = "Exhibits Count"

    def marker_preview(self, obj):
        return format_marker_as_html(obj.marker)
    marker_preview.short_description = "Marker"
    marker_preview.allow_tags = True

    def augmented_preview(self, obj):
        return format_object_as_html(obj.augmented)
    augmented_preview.short_description = "Augmented Object"
    augmented_preview.allow_tags = True


@admin.register(Exhibit)
class ExhibitAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "slug",
        "owner",
        "artworks_count",
        "creation_date",
    ]
    search_fields = ["name", "slug"]
    ordering = ["-creation_date"]

    def get_queryset(self, request):
        queryset = (
            super()
            .get_queryset(request)
            .select_related("owner")
            .prefetch_related("artworks")
        )
        queryset = queryset.annotate(
            _artworks_count=Count("artworks", distinct=True),
        )
        return queryset

    def artworks_count(self, obj):
        return create_link_to_related_artworks(obj, obj.artworks.all())
    artworks_count.short_description = "Artworks Count"
    artworks_count.admin_order_field = "_artworks_count"
    artworks_count.allow_tags = True