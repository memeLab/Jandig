from rest_framework.serializers import ModelSerializer

from core.models import Marker


class MarkerSerializer(ModelSerializer):

    class Meta:
        model = Marker
        fields = ('id', 'owner', 'source', 'uploaded_at', 'author', 'title', 'patt')
        read_only_fields = ('id', 'uploaded_at',)
