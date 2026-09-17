import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from core.forms import MAX_FEEDBACK_ATTACHMENT_BYTES
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
