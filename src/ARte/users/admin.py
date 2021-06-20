from django.contrib import admin
from users.models import Profile
from core.models import Artwork, Object

admin.site.register(Artwork)
admin.site.register(Profile)
admin.site.register(Object)