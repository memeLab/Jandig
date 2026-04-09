from django.contrib import admin
from django.utils.html import format_html

from blog.models import IMAGE_BASE_PATH, Category, Clipping, Post, PostImage

admin.site.register(Category)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "created")
    raw_id_fields = ("author",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("author")


@admin.register(Clipping)
class ClippingAdmin(admin.ModelAdmin):
    list_display = ("title", "id", "created", "modified", "display_date")
    ordering = ("-created",)


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ("image", "copy_button", "filename", "description", "created")
    ordering = ("-created",)

    def filename(self, obj):
        return obj.file.name.lstrip(IMAGE_BASE_PATH)

    def image(self, obj):
        if obj.file:
            return format_html('<img src="{}" width="100" />', obj.file.url)
        return ""

    def copy_button(self, obj):
        if obj.file:
            return format_html(
                '<button type="button" onclick="navigator.clipboard.writeText(\'{}\')">Copy URL</button>',
                obj.file.url,
            )
        return ""
