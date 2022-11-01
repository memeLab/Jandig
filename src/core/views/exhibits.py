from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from core.models import Exhibit
from core.serializers.exhibits import ExhibitSerializer


class ExhibitViewset(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = ExhibitSerializer
    queryset = Exhibit.objects.all().order_by("id")
