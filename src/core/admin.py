from django.contrib import admin

from django.urls import reverse
from django.db.models import Count
from core.models import Artwork, Exhibit, Marker, Object

from django.utils.html import format_html

admin.site.register(Exhibit)
admin.site.register(Object)
admin.site.register(Artwork)


@admin.register(Marker)
class MarkerAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "image_preview",
        "id",
        "owner",
        "author",
        "artworks_count",
        "exhibits_count",
        "uploaded_at",
        "file_size",
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
        """Link to related Artworks"""
        if obj.artworks_count == 0:
            return obj._artworks_count
        # Artwork IDs split by commas
        artworks_list = obj.artworks_list.values_list("id", flat=True)
        artworks_list = ",".join([str(i) for i in artworks_list])

        link = reverse("admin:index") + "core/artwork/?id__in=" + str(artworks_list)
        return format_html('<a href="{}">{}</a>', link, obj._artworks_count)

    def exhibits_count(self, obj):
        return obj._exhibits_count

    def image_preview(self, obj):
        return format_html(
            '<img src="{}" style="height:200px; width:200px;"/>', obj.source.url
        )

    artworks_count.admin_order_field = "_artworks_count"
    exhibits_count.admin_order_field = "_exhibits_count"
