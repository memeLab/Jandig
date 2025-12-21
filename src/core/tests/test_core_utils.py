from django.test import TestCase

from core import utils
from src.config.settings import DJANGO_ADMIN_URL, HEALTH_CHECK_URL, traces_sampler


class CoreUtilsTests(TestCase):
    def test_generate_uuid(self):
        uuid = utils.generate_uuid_name()
        self.assertIsInstance(uuid, str)
        self.assertEqual(len(uuid), 36)  # UUID4 standard length

    def test_get_admin_url(self):
        url = utils.get_admin_url()
        self.assertEqual(url, "/admin/")

    def test_traces_sampler_excludes_admin_and_healthcheck_asgi(self):
        sampling_context = {"asgi_scope": {"path": "/some/other/path/"}}
        rate = traces_sampler(sampling_context)
        assert rate != 0
        sampling_context["asgi_scope"]["path"] = f"/{DJANGO_ADMIN_URL}"
        rate = traces_sampler(sampling_context)
        assert rate == 0
        sampling_context["asgi_scope"]["path"] = f"/{HEALTH_CHECK_URL}"
        rate = traces_sampler(sampling_context)
        assert rate == 0

    def test_traces_sampler_excludes_admin_and_healthcheck_wsgi(self):
        sampling_context = {"wsgi_environ": {"PATH_INFO": "/some/other/path/"}}
        rate = traces_sampler(sampling_context)
        assert rate != 0
        sampling_context["wsgi_environ"]["PATH_INFO"] = f"/{DJANGO_ADMIN_URL}"
        rate = traces_sampler(sampling_context)
        assert rate == 0
        sampling_context["wsgi_environ"]["PATH_INFO"] = f"/{HEALTH_CHECK_URL}"
        rate = traces_sampler(sampling_context)
        assert rate == 0
