from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from users.models import Profile

admin.site.unregister(User)


class NoArtFilter(admin.SimpleListFilter):
    title = "Art Qtdy"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "art_qtd"

    def lookups(self, request, model_admin):
        return [
            ("no_artwork", "Zero Artworks"),
            ("no_marker", "Zero Markers"),
            ("no_objects", "Zero Objects"),
            ("no_exhibits", "Zero Exhibits"),
            ("no_art", "Zero Content"),
        ]

    def queryset(self, request, queryset):
        conditions = Q()
        if not self.value():
            return queryset
        query = self.value().split(",")
        if "no_artwork" in query:
            conditions &= Q(_artworks_count=0)
        if "no_marker" in query:
            conditions &= Q(_markers_count=0)
        if "no_objects" in query:
            conditions &= Q(_ar_objects_count=0)
        if "no_exhibits" in query:
            conditions &= Q(_exhibits_count=0)
        if "no_art" in query:
            return queryset.filter(
                Q(_artworks_count=0)
                & Q(_ar_objects_count=0)
                & Q(_exhibits_count=0)
                & Q(_markers_count=0)
            )

        # Apply the filter
        filtered_queryset = queryset.filter(conditions)
        return filtered_queryset


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user_link",
        "artworks_count",
        "markers_count",
        "ar_objects_count",
        "exhibits_count",
        "created",
        "last_login",
    ]
    ordering = ["-id"]
    list_filter = [NoArtFilter]

    def get_queryset(self, request):
        queryset = (
            super()
            .get_queryset(request)
            .select_related("user")
            .prefetch_related("artworks", "markers", "exhibits", "ar_objects")
        )
        queryset = queryset.annotate(
            _markers_count=Count("markers", distinct=True),
            _artworks_count=Count("artworks", distinct=True),
            _ar_objects_count=Count("ar_objects", distinct=True),
            _exhibits_count=Count("exhibits", distinct=True),
        )
        return queryset

    def username(self, obj):
        return obj.user.username

    def created(self, obj):
        return obj.user.date_joined

    def last_login(self, obj):
        return obj.user.last_login

    def user_link(self, obj):
        """Link to related User"""
        link = reverse("admin:index") + "auth/user/?id=" + str(obj.user.id)
        return format_html('<a href="{}">{}</a>', link, obj.user.username)

    def artworks_count(self, obj):
        return obj._artworks_count

    def markers_count(self, obj):
        return obj._markers_count

    def ar_objects_count(self, obj):
        return obj._ar_objects_count

    def exhibits_count(self, obj):
        return obj._exhibits_count

    artworks_count.admin_order_field = "_artworks_count"
    markers_count.admin_order_field = "_markers_count"
    ar_objects_count.admin_order_field = "_ar_objects_count"
    exhibits_count.admin_order_field = "_exhibits_count"


@admin.register(User)
class JandigUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "profile_link",
        "last_login",
        "date_joined",
        "is_staff",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        queryset = super().get_queryset(request).select_related("profile")
        return queryset

    def profile_link(self, obj):
        """Link to related Profile"""
        link = reverse("admin:index") + "users/profile/?id=" + str(obj.profile.id)
        return format_html('<a href="{}">{}</a>', link, obj.username)
