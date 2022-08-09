from rest_framework.generics import ListAPIView

from core.renderers import JinjaBrowsableAPIRenderer
from core.models import Marker
from core.serializers.markers import MarkerSerializer


class MarkerListAPIView(ListAPIView):
    renderer_classes = [JinjaBrowsableAPIRenderer]
    template_name = 'core/collection.jinja2'
    queryset = Marker.objects.all()
    serializer_class = MarkerSerializer
