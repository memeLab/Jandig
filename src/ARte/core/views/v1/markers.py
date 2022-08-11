from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.renderers import JSONRenderer

from core.renderers import JinjaBrowsableAPIRenderer
from core.models import Marker
from core.serializers.markers import MarkerSerializer


class MarkerListAPIView(ListAPIView):
    renderer_classes = [JinjaBrowsableAPIRenderer]
    template_name = 'core/collection.jinja2'
    queryset = Marker.objects.all()
    serializer_class = MarkerSerializer

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context |= {
            'markers': self.get_queryset(),
            'seeall': True
        }
        return context
