from django.contrib import admin

from blog.models import Category, Clipping, Post, PostImage

admin.site.register(Category)
admin.site.register(PostImage)
admin.site.register(Clipping)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "created", "updated")
    raw_id_fields = ("author",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("author")
