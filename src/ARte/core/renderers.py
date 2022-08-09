from django.shortcuts import render

from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework import status


class JinjaBrowsableAPIRenderer(BrowsableAPIRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        self.accepted_media_type = accepted_media_type or ''
        self.renderer_context = renderer_context or {}
        
        context = self.get_context(data, accepted_media_type, renderer_context)
        view = self.renderer_context['view']
        return render(context['request'], view.template_name, context)
