from blog.models import Category, Post, PostImage
from django.contrib import admin

admin.site.register(Category)
admin.site.register(PostImage)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "created", "updated")
    raw_id_fields = ("author",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("author")
