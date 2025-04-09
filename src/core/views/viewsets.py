from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from core.models import Artwork, Exhibit, Marker, Object
from core.serializers import (
    ArtworkSerializer,
    ExhibitSerializer,
    MarkerSerializer,
    ObjectSerializer,
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
    queryset = Exhibit.objects.all().order_by("id")


class MarkerViewset(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = MarkerSerializer
    queryset = (
        Marker.objects.select_related("owner__user")
        .prefetch_related("artworks__exhibits")
        .all()
        .order_by("id")
    )


class ObjectViewset(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = ObjectSerializer
    queryset = (
        Object.objects.select_related("owner__user")
        .prefetch_related("artworks__exhibits")
        .all()
        .order_by("id")
    )
