from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect, render
from django.core.paginator import Paginator

from core.models import Marker
from core.serializers.markers import MarkerSerializer


class MarkerViewset(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = MarkerSerializer
    queryset = Marker.objects.all().order_by("id")

    @require_http_methods(["GET"])
    def see_markers(request):
        all_markers = Marker.objects.all().order_by("id")
        marker_paginator = Paginator(all_markers, 3)
        marker_page_number = request.GET.get("page", 1)
        marker_list = marker_paginator.get_page(marker_page_number)
        ctx = {
            "markers": marker_list,
            "seeall": True,
        }
        return render(request, "core/collection.jinja2", ctx)
