from django.core.paginator import Paginator
from django.conf import settings

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.renderers import JSONRenderer

from core.renderers import JinjaBrowsableAPIRenderer
from core.models import Marker
from core.serializers.markers import MarkerSerializer


class MarkerListAPIView(ListAPIView):
    renderer_classes = [JinjaBrowsableAPIRenderer]
    template_name = 'core/collection.jinja2'
    queryset = Marker.objects.all().order_by('id')
    serializer_class = MarkerSerializer

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context |= {
            'markers': Paginator(
                self.get_queryset(), settings.PAGE_SIZE).object_list,
            'seeall': True
        }
        return context


class MarkerRetrieveUpdateAPIViewAPIView(RetrieveAPIView):
    renderer_classes = [JSONRenderer]
    queryset = Marker.objects.all()
    serializer_class = MarkerSerializer
