from django.contrib import admin

from core.models import Artwork, Exhibit, Marker, Object

admin.site.register(Exhibit)
admin.site.register(Object)
admin.site.register(Marker)
admin.site.register(Artwork)
