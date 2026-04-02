from django.forms import Widget

WYSIWYG_CLASSES = [
]
class RichTextEditorWidget(Widget):
    template_name = "trix_widget.html"

    class Media:
        css = {"all": ("forms/css/trix.css",)}
        js = (
            "forms/js/trix_2.1.1.js",
            "forms/js/trix.config.js",
        )

    def __init__(self, attrs=None) -> None:
        super().__init__(attrs)

        self.attrs.update(
            {
                "class": " ".join(
                    [*WYSIWYG_CLASSES, attrs.get("class", "") if attrs else ""]
                )
            }
        )