import io
import re
from unittest.mock import Mock, patch

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from core.forms import FEEDBACK_HONEYPOT_FIELD, MAX_FEEDBACK_ATTACHMENT_BYTES
from core.models import Feedback, FeedbackKinds


def screenshot(name="shot.png"):
    buffer = io.BytesIO()
    Image.new("RGB", (8, 8), "white").save(buffer, format="PNG")
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type="image/png")


class TestFeedbackForm(TestCase):
    def test_the_form_is_reachable_without_an_account(self):
        response = self.client.get(reverse("feedback"))

        assert response.status_code == 200

    def test_a_bug_report_is_stored(self):
        response = self.client.post(
            reverse("feedback"),
            {
                "kind": FeedbackKinds.BUG,
                "description": "The marker preview never loads on Firefox.",
                "email": "someone@example.com",
            },
        )

        assert response.status_code == 200
        report = Feedback.objects.get()
        assert report.kind == FeedbackKinds.BUG
        assert report.email == "someone@example.com"
        assert report.handled is False

    def test_a_feature_request_is_stored_with_its_own_kind(self):
        self.client.post(
            reverse("feedback"),
            {
                "kind": FeedbackKinds.FEATURE,
                "description": "Let me sort exhibits by name.",
            },
        )

        assert Feedback.objects.get().kind == FeedbackKinds.FEATURE

    def test_the_email_is_optional(self):
        self.client.post(
            reverse("feedback"),
            {"kind": FeedbackKinds.BUG, "description": "Something broke."},
        )

        assert Feedback.objects.get().email == ""

    def test_a_description_is_required(self):
        self.client.post(reverse("feedback"), {"kind": FeedbackKinds.BUG})

        assert not Feedback.objects.exists()

    def test_an_attachment_is_stored_under_a_generated_name(self):
        self.client.post(
            reverse("feedback"),
            {
                "kind": FeedbackKinds.BUG,
                "description": "See the screenshot.",
                "attachment": screenshot("Captura de tela #1.png"),
            },
        )
        report = Feedback.objects.get()

        assert report.attachment.name.startswith("feedback/")
        assert report.attachment.name.endswith(".png")
        assert "Captura" not in report.attachment.name

    def test_an_executable_attachment_is_rejected(self):
        self.client.post(
            reverse("feedback"),
            {
                "kind": FeedbackKinds.BUG,
                "description": "Trying to attach a binary.",
                "attachment": SimpleUploadedFile("payload.exe", b"MZ\x00\x00"),
            },
        )

        assert not Feedback.objects.exists()

    def test_an_oversized_attachment_is_rejected(self):
        oversized = SimpleUploadedFile(
            "huge.png", b"\x00" * (MAX_FEEDBACK_ATTACHMENT_BYTES + 1)
        )
        self.client.post(
            reverse("feedback"),
            {
                "kind": FeedbackKinds.BUG,
                "description": "Attaching something enormous.",
                "attachment": oversized,
            },
        )

        assert not Feedback.objects.exists()

    def test_the_footer_links_to_the_form(self):
        response = self.client.get(reverse("home"))

        assert reverse("feedback").encode() in response.content


REPORT = {"kind": FeedbackKinds.BUG, "description": "Something broke."}


def stored_attachments():
    """Names under feedback/ in the storage, which the test run shares."""
    if not default_storage.exists("feedback"):
        return set()
    return set(default_storage.listdir("feedback")[1])


def turnstile_answering(success):
    """Patch Cloudflare's siteverify call to answer `success`."""
    response = Mock()
    response.json.return_value = {"success": success}
    return patch(
        "users.services.turnstile_service.requests.post", return_value=response
    )


class TestFeedbackBotProtection(TestCase):
    """The form is public, so it gets the sign-up form's Turnstile check plus
    a honeypot field."""

    @override_settings(TURNSTILE_ENABLED=True)
    def test_a_report_without_a_turnstile_token_is_rejected(self):
        with turnstile_answering(True) as siteverify:
            response = self.client.post(reverse("feedback"), REPORT)

        assert response.status_code == 400
        assert not Feedback.objects.exists()
        siteverify.assert_not_called()

    @override_settings(TURNSTILE_ENABLED=True)
    def test_a_report_with_a_token_cloudflare_refuses_is_rejected(self):
        with turnstile_answering(False):
            response = self.client.post(
                reverse("feedback"), {**REPORT, "cf-turnstile-response": "forged"}
            )

        assert response.status_code == 400
        assert not Feedback.objects.exists()

    @override_settings(TURNSTILE_ENABLED=True)
    def test_a_rejected_report_does_not_store_its_attachment(self):
        before = stored_attachments()

        with turnstile_answering(False):
            self.client.post(
                reverse("feedback"),
                {
                    **REPORT,
                    "attachment": screenshot(),
                    "cf-turnstile-response": "forged",
                },
            )

        assert stored_attachments() == before

    @override_settings(TURNSTILE_ENABLED=True, TURNSTILE_SECRET_KEY="secret")
    def test_a_report_with_a_token_cloudflare_accepts_is_stored(self):
        with turnstile_answering(True) as siteverify:
            response = self.client.post(
                reverse("feedback"), {**REPORT, "cf-turnstile-response": "genuine"}
            )

        assert response.status_code == 200
        assert Feedback.objects.count() == 1
        assert siteverify.call_args.kwargs["data"] == {
            "secret": "secret",
            "response": "genuine",
        }

    @override_settings(TURNSTILE_ENABLED=True, TURNSTILE_SITE_KEY="site-key")
    def test_the_widget_is_shown_and_holds_the_submit_button(self):
        content = self.client.get(reverse("feedback")).content.decode()

        assert 'class="cf-turnstile"' in content
        assert 'data-sitekey="site-key"' in content
        assert "challenges.cloudflare.com/turnstile" in content
        assert 'id="submit-button" disabled' in content

    @override_settings(TURNSTILE_ENABLED=False)
    def test_the_widget_is_absent_when_turnstile_is_disabled(self):
        content = self.client.get(reverse("feedback")).content.decode()

        assert "cf-turnstile" not in content
        assert 'id="submit-button"' not in content

    @override_settings(TURNSTILE_ENABLED=True)
    def test_the_widget_comes_back_when_the_form_has_errors(self):
        with turnstile_answering(True):
            response = self.client.post(
                reverse("feedback"),
                {"kind": FeedbackKinds.BUG, "cf-turnstile-response": "genuine"},
            )

        assert not Feedback.objects.exists()
        assert 'class="cf-turnstile"' in response.content.decode()

    @override_settings(TURNSTILE_ENABLED=False)
    def test_a_report_that_fills_the_honeypot_is_dropped_quietly(self):
        response = self.client.post(
            reverse("feedback"), {**REPORT, FEEDBACK_HONEYPOT_FIELD: "buy now"}
        )

        # Same answer a real report gets, so the bot learns nothing.
        assert response.status_code == 200
        assert "Thank you" in response.content.decode()
        assert not Feedback.objects.exists()

    @override_settings(TURNSTILE_ENABLED=True)
    def test_the_honeypot_is_checked_before_asking_cloudflare(self):
        with turnstile_answering(True) as siteverify:
            self.client.post(
                reverse("feedback"),
                {
                    **REPORT,
                    FEEDBACK_HONEYPOT_FIELD: "buy now",
                    "cf-turnstile-response": "genuine",
                },
            )

        assert not Feedback.objects.exists()
        siteverify.assert_not_called()

    def test_the_honeypot_is_in_the_form_but_out_of_reach(self):
        content = self.client.get(reverse("feedback")).content.decode()
        field = re.search(
            rf'<input[^>]*name="{FEEDBACK_HONEYPOT_FIELD}"[^>]*>', content
        )

        assert field is not None
        # Not type="hidden": bots skip those. Hidden by its off-screen wrapper.
        assert 'type="text"' in field.group()
        assert 'tabindex="-1"' in field.group()
        assert 'autocomplete="off"' in field.group()
        wrapper = content[: field.start()].rsplit("<div", 1)[1]
        assert 'aria-hidden="true"' in wrapper
        assert "left: -10000px" in wrapper

    def test_an_empty_honeypot_does_not_block_a_real_report(self):
        self.client.post(reverse("feedback"), {**REPORT, FEEDBACK_HONEYPOT_FIELD: ""})

        assert Feedback.objects.count() == 1
