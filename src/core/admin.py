from io import BytesIO

from django.contrib import admin
from django.core.files import File
from django.core.files.base import ContentFile
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from PIL import Image
from pymarker import generate_patt_from_image, remove_borders_from_image

from core.models import Artwork, Exhibit, Marker, Object
from core.views.api_views import MarkerGeneratorAPIView


def create_link_to_related_artworks(obj, artworks_list):
    """Link to related Artworks"""
    if obj._artworks_count == 0:
        return obj._artworks_count
    artworks_list = ",".join([str(artwork.id) for artwork in artworks_list])

    link = reverse("admin:index") + "core/artwork/?id__in=" + str(artworks_list)
    return format_html('<a href="{}">{}</a>', link, obj._artworks_count)


class BaseMarkerObjectAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "image_preview",
        "id",
        "_owner",
        "author",
        "artworks_count",
        "exhibits_count",
        "created",
        "modified",
        "filesize",
    ]
    search_fields = ["title", "id"]
    ordering = ["-created"]

    def get_queryset(self, request):
        queryset = (
            super()
            .get_queryset(request)
            .select_related("owner", "owner__user")
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
    artworks_count.admin_order_field = "_artworks_count"

    def exhibits_count(self, obj):
        return obj._exhibits_count

    exhibits_count.admin_order_field = "_exhibits_count"

    def filesize(self, obj):
        """File size in MB"""
        if obj.file_size > 0:
            return f"{obj.file_size / 1024 / 1024:.2f} MB"
        return obj.file_size

    filesize.short_description = "File Size"
    filesize.admin_order_field = "file_size"

    def _owner(self, obj):
        """Display the owner of the object"""
        link = reverse("admin:index") + "users/profile/?id=" + str(obj.owner.id)
        return format_html('<a href="{}">{}</a>', link, obj.owner.user.username)


@admin.action(description="Regenerate Marker With Inner Border")
def regenerate_marker_white_border(modeladmin, request, queryset):
    """
    Regenerate markers with white inner border.
    This action will regenerate the marker images with a white inner border.
    """
    regenerate_marker(queryset, inner_border=True)


@admin.action(description="Regenerate Marker Without Inner Border")
def regenerate_marker_no_inner_border(modeladmin, request, queryset):
    """Regenerate markers without inner border.
    This action will regenerate the marker images without a white inner border.
    """
    regenerate_marker(queryset, inner_border=False)


def generate_uuid_name():
    """Generate a UUID4 name for the marker."""
    import uuid

    return str(uuid.uuid4())  # Use uuid4 for a random unique identifier


@admin.action(description="Remove Border")
def remove_border(modeladmin, request, queryset):
    """Remove border from markers.
    This action will regenerate the marker images without any borders.
    """
    for marker in queryset:
        with Image.open(marker.source) as image:
            pil_image = remove_borders_from_image(image)
            blob = BytesIO()
            pil_image.save(blob, "JPEG")
            uuid = generate_uuid_name()
            filename = f"{uuid}.jpg"
            marker.file_size = marker.source.size
            marker.source.save(filename, File(blob), save=True)
            patt_str = generate_patt_from_image(pil_image)
            marker.patt.save(
                f"{uuid}.patt",
                ContentFile(patt_str.encode("utf-8")),
                save=True,
            )
        marker.save()


def regenerate_marker(queryset, inner_border=False):
    for marker in queryset:
        with Image.open(marker.source) as image:
            pil_image = MarkerGeneratorAPIView.generate_marker(
                image, inner_border=inner_border
            )
            blob = BytesIO()
            pil_image.save(blob, "JPEG")
            uuid = generate_uuid_name()
            filename = f"{uuid}.jpg"
            marker.file_size = marker.source.size
            marker.source.save(filename, File(blob), save=True)
            patt_str = generate_patt_from_image(image)
            marker.patt.save(
                f"{uuid}.patt",
                ContentFile(patt_str.encode("utf-8")),
                save=True,
            )
        marker.save()


@admin.register(Marker)
class MarkerAdmin(BaseMarkerObjectAdmin):
    actions = [
        regenerate_marker_white_border,
        regenerate_marker_no_inner_border,
        remove_border,
    ]

    def image_preview(self, obj):
        return format_html(obj.as_html_thumbnail())


@admin.register(Object)
class ObjectAdmin(BaseMarkerObjectAdmin):
    list_display = BaseMarkerObjectAdmin.list_display + ["scale", "position"]

    def image_preview(self, obj):
        return format_html(obj.as_html_thumbnail())


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "id",
        "_author",
        "marker_preview",
        "augmented_preview",
        "exhibits_count",
        "created",
        "modified",
    ]
    search_fields = ["title", "id"]
    ordering = ["-created"]

    def get_queryset(self, request):
        queryset = (
            super()
            .get_queryset(request)
            .select_related("author", "author__user", "marker", "augmented")
            .prefetch_related("exhibits")
        )
        queryset = queryset.annotate(
            _exhibits_count=Count("exhibits", distinct=True),
        )
        return queryset

    def exhibits_count(self, obj):
        """Link to related Artworks"""
        if obj._exhibits_count == 0:
            return obj._exhibits_count
        exhibit_list = ",".join([str(exhibit.id) for exhibit in obj.exhibits.all()])

        link = reverse("admin:index") + "core/exhibit/?id__in=" + str(exhibit_list)
        return format_html('<a href="{}">{}</a>', link, obj._exhibits_count)

    exhibits_count.admin_order_field = "_exhibits_count"
    exhibits_count.short_description = "Exhibits Count"

    def marker_preview(self, obj):
        return format_html(obj.marker.as_html_thumbnail())

    marker_preview.short_description = "Marker"
    marker_preview.allow_tags = True

    def augmented_preview(self, obj):
        return format_html(obj.augmented.as_html_thumbnail())

    augmented_preview.short_description = "Augmented Object"
    augmented_preview.allow_tags = True

    def _author(self, obj):
        """Display the author of the Artwork"""
        link = reverse("admin:index") + "users/profile/?id=" + str(obj.author.id)
        return format_html('<a href="{}">{}</a>', link, obj.author.user.username)


@admin.register(Exhibit)
class ExhibitAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "slug",
        "_owner",
        "artworks_count",
        "created",
        "modified",
    ]
    search_fields = ["name", "slug"]
    ordering = ["-created"]

    def get_queryset(self, request):
        queryset = (
            super()
            .get_queryset(request)
            .select_related("owner", "owner__user")
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

    def _owner(self, obj):
        """Display the owner of the object"""
        link = reverse("admin:index") + "users/profile/?id=" + str(obj.owner.id)
        return format_html('<a href="{}">{}</a>', link, obj.owner.user.username)
