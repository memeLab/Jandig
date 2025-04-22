from rest_framework.renderers import TemplateHTMLRenderer


class ModalHTMLRenderer(TemplateHTMLRenderer):
    """
    Custom renderer to render HTML templates for modals.
    """

    media_type = "text/html"
    format = "modal"
    charset = "utf-8"
