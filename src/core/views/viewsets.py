from django.db.models import Count
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from core.models import Artwork, Exhibit, Marker, Object
from core.serializers import (
    ArtworkSerializer,
    ExhibitSerializer,
    MarkerSerializer,
    ObjectSerializer,
)


class MarkerViewset(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = MarkerSerializer
    queryset = (
        Marker.objects.select_related("owner__user")
        .prefetch_related("artworks__exhibits")
        .annotate(exhibits_count=Count("artworks__exhibits", distinct=True))
        .all()
        .order_by("id")
    )


class ObjectViewset(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = ObjectSerializer
    queryset = (
        Object.objects.select_related("owner__user")
        .prefetch_related("artworks__exhibits")
        .annotate(exhibits_count=Count("artworks__exhibits", distinct=True))
        .all()
        .order_by("id")
    )


class ArtworkViewset(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = ArtworkSerializer
    queryset = (
        Artwork.objects.prefetch_related(
            "exhibits", "marker__artworks", "augmented__artworks"
        )
        .select_related(
            "author__user",
            "marker__owner__user",
            "augmented__owner__user",
        )
        .all()
        .order_by("id")
    )


class ExhibitViewset(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = ExhibitSerializer

    def get_queryset(self):
        queryset = (
            Exhibit.objects.prefetch_related(
                "artworks__exhibits",
                "artworks__author__user",
                "artworks__marker__artworks",
                "artworks__marker__owner__user",
                "artworks__augmented__artworks",
                "artworks__augmented__owner__user",
            )
            .all()
            .order_by("id")
        )
        owner_id = self.request.query_params.get("owner")
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(name__icontains=search)
        if owner_id is not None:
            try:
                owner_id = int(owner_id)
            except ValueError:
                # Handle the case where owner_id is not a valid integer
                return queryset.none()
            queryset = queryset.filter(owner=owner_id)
        return queryset
