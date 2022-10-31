from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from core.models import Artwork
from core.serializers.artworks import ArtworkSerializer


class ArtworkViewset(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = ArtworkSerializer
    queryset = Artwork.objects.all().order_by("id")
