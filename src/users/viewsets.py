from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from users.models import Profile
from users.serializers import ProfileSerializer


class ProfileViewset(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = ProfileSerializer

    def get_queryset(self):
        """Optionally finds profile based on user id"""
        queryset = Profile.objects.select_related("user").all()
        user_id = self.request.query_params.get("user", None)
        if user_id:
            try:
                user_id = int(user_id)
            except ValueError:
                return queryset.none()
            return queryset.filter(user__id=user_id)
        return queryset
