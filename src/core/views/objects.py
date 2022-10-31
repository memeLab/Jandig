from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from core.models import Object
from core.serializers.objects import ObjectSerializer


class ObjectViewset(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = ObjectSerializer
    queryset = Object.objects.all().order_by("id")
