from django.shortcuts import render
from rest_framework import status
from rest_framework.renderers import BrowsableAPIRenderer


class JinjaBrowsableAPIRenderer(BrowsableAPIRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        self.accepted_media_type = accepted_media_type or ""
        self.renderer_context = renderer_context or {}

        request = self.renderer_context["request"]
        view = self.renderer_context["view"]

        response = renderer_context["response"]
        if response.status_code == status.HTTP_204_NO_CONTENT:
            response.status_code = status.HTTP_200_OK

        return render(request, view.template_name, self.renderer_context)
