from django.contrib import admin

from blog.models import Post, Category

admin.site.register(Category)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    raw_id_fields=("author",)
    def get_queryset(self, request):
        return super().get_queryset(request).select_related("author")