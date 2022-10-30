from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django.utils import translation
from django.conf import settings

from jinja2 import Environment


def environment(**options):
    options["extensions"] = ["jinja2.ext.i18n"]
    env = Environment(**options)

    env.globals.update(
        {
            "static": staticfiles_storage.url,
            "url": reverse,
            "LANGUAGES": settings.LANGUAGES,
            "CUR_LANGUAGE": translation.get_language(),
        }
    )

    env.install_gettext_translations(translation, newstyle=True)
    return env
