from django.contrib import admin

from users.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display=["id", "username", "email", "created"]
    ordering=["-id"]
    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")
    
    def username(self, obj):
        return obj.user.username
    
    def email(self,obj):
        return obj.user.email
    
    def created(self,obj):
        return obj.user.date_joined