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
        Artwork.objects.all()
        .select_related("marker", "augmented", "author")
        .order_by("id")
    )


class ExhibitViewset(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = ExhibitSerializer
    queryset = Exhibit.objects.all().order_by("id")


class MarkerViewset(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = MarkerSerializer
    queryset = Marker.objects.all().order_by("id")


class ObjectViewset(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = ObjectSerializer
    queryset = Object.objects.all().order_by("id")
