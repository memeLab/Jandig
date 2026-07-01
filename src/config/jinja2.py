from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django.utils import translation
from jinja2 import Environment


def filesizeformat(value):
    """Format a file size in bytes to a human-readable string."""
    try:
        size = float(value)
    except (TypeError, ValueError):
        return "0 B"
    if size < 1024:
        return f"{int(size)} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.1f} GB"


def environment(**options):
    options["extensions"] = ["jinja2.ext.i18n"]
    env = Environment(**options)

    env.globals.update(
        {
            "static": staticfiles_storage.url,
            "url": reverse,
            "enumerate": enumerate,
            "CUR_LANGUAGE": translation.get_language(),
            "languages": [
                translation.get_language_info(code)
                for code, _name in settings.LANGUAGES
            ],
        }
    )

    env.filters["filesizeformat"] = filesizeformat

    env.install_gettext_translations(translation, newstyle=True)
    return env
