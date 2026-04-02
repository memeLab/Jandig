from django.contrib import admin

from blog.models import Category, Clipping, Post, PostImage
from blog.widgets import RichTextEditorWidget
from django import forms
admin.site.register(Category)
admin.site.register(PostImage)

class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = "__all__"
        widgets = {
            "body": RichTextEditorWidget,
        }

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "created")
    form = PostAdminForm
    raw_id_fields = ("author",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("author")


@admin.register(Clipping)
class ClippingAdmin(admin.ModelAdmin):
    list_display = ("title", "id", "created", "modified", "display_date")
    ordering = ("-created",)
