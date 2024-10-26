from core.models import Marker
from core.serializers.markers import MarkerSerializer
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet


class MarkerViewset(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = MarkerSerializer
    queryset = Marker.objects.all().order_by("id")
