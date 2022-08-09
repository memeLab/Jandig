from rest_framework.serializers import ModelSerializer

from core.models import Marker


class MarkerSerializer(ModelSerializer):

    class Meta:
        model = Marker
        fields = ('owner', 'source', 'upload_at', 'author', 'title', 'patt')
