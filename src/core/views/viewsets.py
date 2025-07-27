from django.db.models import Count
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.renderers import (
    BrowsableAPIRenderer,
    JSONRenderer,
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.models import Artwork, Exhibit, Marker, Object
from core.renderers import ModalHTMLRenderer
from core.serializers import (
    ArtworkSerializer,
    ExhibitSerializer,
    MarkerSerializer,
    ObjectSerializer,
)


class MarkerViewset(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = MarkerSerializer
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, ModalHTMLRenderer]
    queryset = (
        Marker.objects.select_related("owner__user")
        .prefetch_related("artworks__exhibits")
        .annotate(exhibits_count=Count("artworks__exhibits", distinct=True))
        .all()
        .order_by("id")
    )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.accepted_renderer.format == "modal":
            ctx = {"marker": instance}
            if request.GET.get("go_back_url"):
                ctx["go_back_url"] = request.GET.get("go_back_url")
            return Response(ctx, template_name="core/templates/marker_modal.jinja2")
        return super().retrieve(request, *args, **kwargs)


class ObjectViewset(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = ObjectSerializer
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, ModalHTMLRenderer]
    queryset = (
        Object.objects.select_related("owner__user")
        .prefetch_related("artworks__exhibits")
        .annotate(exhibits_count=Count("artworks__exhibits", distinct=True))
        .all()
        .order_by("id")
    )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.accepted_renderer.format == "modal":
            ctx = {"ar_object": instance}
            if request.GET.get("go_back_url"):
                ctx["go_back_url"] = request.GET.get("go_back_url")
            return Response(
                ctx,
                template_name="core/templates/object_modal.jinja2",
            )
        return super().retrieve(request, *args, **kwargs)


class ArtworkViewset(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = ArtworkSerializer
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, ModalHTMLRenderer]
    queryset = (
        Artwork.objects.prefetch_related(
            "exhibits", "marker__artworks", "augmented__artworks"
        )
        .select_related(
            "author__user",
            "marker__owner__user",
            "augmented__owner__user",
        )
        .all()
        .order_by("id")
    )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.accepted_renderer.format == "modal":
            return Response(
                {"artwork": instance},
                template_name="core/templates/artwork_modal.jinja2",
            )
        return super().retrieve(request, *args, **kwargs)


class ExhibitViewset(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = ExhibitSerializer

    def get_queryset(self):
        queryset = (
            Exhibit.objects.prefetch_related(
                "artworks__exhibits",
                "artworks__author__user",
                "artworks__marker__artworks",
                "artworks__marker__owner__user",
                "artworks__augmented__artworks",
                "artworks__augmented__owner__user",
                "augmenteds__exhibits",
            )
            .all()
            .order_by("id")
        )
        owner_id = self.request.query_params.get("owner")
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(name__icontains=search)
        if owner_id is not None:
            try:
                owner_id = int(owner_id)
            except ValueError:
                # Handle the case where owner_id is not a valid integer
                return queryset.none()
            queryset = queryset.filter(owner=owner_id)
        return queryset
