from io import BytesIO

from django.contrib import admin
from django.core.files import File
from django.core.files.base import ContentFile
from django.db.models import Count
from django.utils.html import format_html
from PIL import Image
from pymarker import generate_patt_from_image, remove_borders_from_image

from core.models import Artwork, Exhibit, Marker, Object, Sound
from core.utils import generate_uuid_name, get_admin_url
from core.views.api_views import MarkerGeneratorAPIView

HTML_LINK = '<a href="{}">{}</a>'


def get_user_profile_path():
    """Get the user profile path"""
    return get_admin_url() + "users/profile/?id={}"


def create_link_to_related_artworks(obj, artworks_list):
    """Link to related Artworks"""
    if obj._artworks_count == 0:
        return obj._artworks_count
    artworks_list = ",".join([str(artwork.id) for artwork in artworks_list])

    link = get_admin_url() + "core/artwork/?id__in=" + str(artworks_list)
    return format_html(HTML_LINK, link, obj._artworks_count)


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
        link = get_user_profile_path().format(obj.owner.id)
        return format_html(HTML_LINK, link, obj.owner.user.username)


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
    list_display = BaseMarkerObjectAdmin.list_display + [
        "file_extension",
    ]
    search_fields = ["title", "id"]
    list_filter = ["file_extension"]

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
        "scale",
        "position",
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

        link = get_admin_url() + "core/exhibit/?id__in=" + str(exhibit_list)
        return format_html(HTML_LINK, link, obj._exhibits_count)

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
        link = get_user_profile_path().format(obj.author.id)
        return format_html(HTML_LINK, link, obj.author.user.username)

    def scale(self, obj):
        """Display the scale of the artwork"""
        return f"{obj.scale_x} x {obj.scale_y}"

    def position(self, obj):
        """Display the position of the artwork"""
        return f"x: {obj.position_x} y: {obj.position_y}"


@admin.register(Exhibit)
class ExhibitAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "slug",
        "_owner",
        "artworks_count",
        "augmenteds_count",
        "created",
        "modified",
    ]
    list_filter = ["exhibit_type"]
    search_fields = ["name", "slug"]
    ordering = ["-created"]

    def get_queryset(self, request):
        queryset = (
            super()
            .get_queryset(request)
            .select_related("owner", "owner__user")
            .prefetch_related("artworks", "augmenteds")
        )
        queryset = queryset.annotate(
            _artworks_count=Count("artworks", distinct=True),
            _augmenteds_count=Count("augmenteds", distinct=True),
        )
        return queryset

    def artworks_count(self, obj):
        return create_link_to_related_artworks(obj, obj.artworks.all())

    artworks_count.short_description = "Artworks Count"
    artworks_count.admin_order_field = "_artworks_count"
    artworks_count.allow_tags = True

    def augmenteds_count(self, obj):
        """Count of Objects in the exhibit"""
        if obj._augmenteds_count == 0:
            return obj._augmenteds_count
        augmenteds_list = ",".join(
            [str(augmented.id) for augmented in obj.augmenteds.all()]
        )

        link = get_admin_url() + "core/object/?id__in=" + str(augmenteds_list)
        return format_html(HTML_LINK, link, obj._augmenteds_count)

    augmenteds_count.short_description = "Augmenteds Count"
    augmenteds_count.admin_order_field = "_augmenteds_count"
    augmenteds_count.allow_tags = True

    def _owner(self, obj):
        """Display the owner of the object"""
        link = get_user_profile_path().format(obj.owner.id)
        return format_html(HTML_LINK, link, obj.owner.user.username)


@admin.register(Sound)
class SoundAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "preview",
        "_owner",
        "created",
        "modified",
    ]

    def _owner(self, obj):
        """Display the owner of the object"""
        link = get_user_profile_path().format(obj.owner.id)
        return format_html(HTML_LINK, link, obj.owner.user.username)

    def preview(self, obj):
        return format_html(obj.as_html_thumbnail().replace(obj.title, ""))
