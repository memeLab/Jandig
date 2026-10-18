"""Byte-size limits for uploads (#1010)."""

from unittest import mock

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from core.forms import (
    SoundForm,
    UploadMarkerForm,
    UploadObjectForm,
    file_has_changed,
)
from core.models import Object, Sound
from core.tests.factory import ObjectFactory, SoundFactory
from core.tests.utils import SQUARE_SVG, get_example_object, get_example_sound
from core.tests.utils import png_bytes as build_png_bytes
from core.upload_limits import MB, format_size
from users.models import Profile, User

# Small limits so the tests never need megabyte-sized fixtures. The checks
# only look at file.size, so padded or fake content is enough.
TINY = 1000


def upload(name, size, content_type="application/octet-stream"):
    return SimpleUploadedFile(name, b"\0" * size, content_type=content_type)


class TestDefaultLimits(TestCase):
    def test_defaults_match_the_agreed_values(self):
        assert settings.MAX_SVG_MARKER_UPLOAD_SIZE == 1 * MB
        assert settings.MAX_RASTER_MARKER_UPLOAD_SIZE == 20 * MB
        assert settings.MAX_IMAGE_OBJECT_UPLOAD_SIZE == 2 * MB
        assert settings.MAX_VIDEO_OBJECT_UPLOAD_SIZE == 30 * MB
        assert settings.MAX_GLB_OBJECT_UPLOAD_SIZE == 30 * MB
        assert settings.MAX_AUDIO_UPLOAD_SIZE == 15 * MB
        assert settings.MAX_THUMBNAIL_UPLOAD_SIZE == 2 * MB
        assert settings.MAX_THUMBNAIL_DIMENSION == 2048

    def test_request_ceiling_fits_the_largest_form(self):
        # An object upload can carry a video or GLB, its thumbnail and an
        # audio description at once.
        largest_object_form = (
            max(
                settings.MAX_VIDEO_OBJECT_UPLOAD_SIZE,
                settings.MAX_GLB_OBJECT_UPLOAD_SIZE,
            )
            + settings.MAX_THUMBNAIL_UPLOAD_SIZE
            + settings.MAX_AUDIO_UPLOAD_SIZE
        )
        assert settings.MAX_REQUEST_BODY_SIZE > largest_object_form


class TestFormatSize(TestCase):
    def test_whole_megabytes_have_no_decimal(self):
        assert format_size(20 * MB) == "20 MB"

    def test_sizes_round_up(self):
        # Just over the limit must not read as equal to it.
        assert format_size(MB + 1) == "1.1 MB"
        assert format_size(int(23.41 * MB)) == "23.5 MB"

    def test_small_sizes(self):
        assert format_size(TINY) == "1000 B"
        assert format_size(1536) == "1.5 KB"


class TestMarkerSizeLimit(TestCase):
    def marker_form(self, source):
        return UploadMarkerForm(
            data={"title": "Marker", "author": "Test Author"},
            files={"source": source},
        )

    @override_settings(MAX_SVG_MARKER_UPLOAD_SIZE=TINY)
    def test_form_rejects_an_svg_over_the_limit(self):
        svg = SQUARE_SVG + b"<!--" + b" " * TINY + b"-->"
        form = self.marker_form(
            SimpleUploadedFile("big.svg", svg, content_type="image/svg+xml")
        )

        assert not form.is_valid()
        assert "SVG markers are limited to 1000 B" in form.errors["source"][0]

    @override_settings(MAX_SVG_MARKER_UPLOAD_SIZE=TINY)
    def test_svg_is_rejected_before_it_is_parsed(self):
        with mock.patch("core.forms.rasterize_svg") as rasterize:
            form = self.marker_form(upload("big.svg", TINY + 1, "image/svg+xml"))
            assert not form.is_valid()
        rasterize.assert_not_called()

    @override_settings(MAX_RASTER_MARKER_UPLOAD_SIZE=TINY)
    def test_form_rejects_a_raster_over_the_limit(self):
        png = build_png_bytes(64, 64) + b"\0" * TINY
        form = self.marker_form(
            SimpleUploadedFile("big.png", png, content_type="image/png")
        )

        assert not form.is_valid()
        assert "Marker images are limited to 1000 B" in form.errors["source"][0]

    @override_settings(MAX_RASTER_MARKER_UPLOAD_SIZE=10)
    def test_svg_is_held_to_the_svg_limit_not_the_raster_one(self):
        # The PNG rasterised from the SVG is not an upload, so the raster
        # limit does not apply to it either.
        form = self.marker_form(
            SimpleUploadedFile("marker.svg", SQUARE_SVG, content_type="image/svg+xml")
        )

        assert form.is_valid(), form.errors

    def test_form_accepts_a_marker_under_the_limits(self):
        form = self.marker_form(
            SimpleUploadedFile(
                "marker.png", build_png_bytes(64, 64), content_type="image/png"
            )
        )

        assert form.is_valid(), form.errors


class TestMarkerGeneratorSizeLimit(TestCase):
    @override_settings(MAX_SVG_MARKER_UPLOAD_SIZE=TINY)
    def test_preview_rejects_an_svg_over_the_limit(self):
        with mock.patch("core.views.api_views.rasterize_svg") as rasterize:
            response = self.client.post(
                reverse("markergenerator"),
                {"source": upload("big.svg", TINY + 1, "image/svg+xml")},
            )
        assert response.status_code == 400
        assert "SVG markers are limited to 1000 B" in response.data["error"]
        rasterize.assert_not_called()

    @override_settings(MAX_RASTER_MARKER_UPLOAD_SIZE=TINY)
    def test_preview_rejects_a_raster_over_the_limit(self):
        response = self.client.post(
            reverse("markergenerator"),
            {"source": upload("big.png", TINY + 1, "image/png")},
        )
        assert response.status_code == 400
        assert "Marker images are limited to 1000 B" in response.data["error"]


@override_settings(
    MAX_IMAGE_OBJECT_UPLOAD_SIZE=TINY,
    MAX_VIDEO_OBJECT_UPLOAD_SIZE=TINY,
    MAX_GLB_OBJECT_UPLOAD_SIZE=TINY,
    MAX_AUDIO_UPLOAD_SIZE=TINY,
)
class TestObjectSizeLimit(TestCase):
    def object_form(self, **files):
        return UploadObjectForm(
            data={"title": "Object", "author": "Test Author"}, files=files
        )

    def assert_source_rejected(self, name, expected):
        form = self.object_form(source=upload(name, TINY + 1))

        assert not form.is_valid()
        assert expected in form.errors["source"][0]

    def test_rejects_a_gif_over_the_limit(self):
        self.assert_source_rejected("big.gif", "GIF and PNG objects are limited")

    def test_rejects_a_png_over_the_limit(self):
        self.assert_source_rejected("big.png", "GIF and PNG objects are limited")

    def test_rejects_an_mp4_over_the_limit(self):
        self.assert_source_rejected("big.mp4", "MP4 and WebM videos are limited")

    def test_rejects_a_webm_over_the_limit(self):
        self.assert_source_rejected("big.webm", "MP4 and WebM videos are limited")

    def test_rejects_a_glb_over_the_limit(self):
        self.assert_source_rejected("big.glb", "GLB models are limited")

    def test_accepts_a_file_exactly_at_the_limit(self):
        form = self.object_form(source=upload("ok.mp4", TINY))

        assert "source" not in form.errors

    def test_rejects_an_audio_description_over_the_limit(self):
        form = self.object_form(
            source=upload("ok.mp4", 10),
            audio_description=upload("big.mp3", TINY + 1),
        )

        assert not form.is_valid()
        assert "Audio files are limited" in form.errors["audio_description"][0]

    def test_editing_without_replacing_the_file_skips_the_limit(self):
        # Stored before the limits existed, and larger than TINY.
        profile = Profile.objects.get(
            user=User.objects.create_user(username="owner", password="pw")
        )
        obj = ObjectFactory(
            source=get_example_object("flyingsaucer.gif"), owner=profile
        )
        assert obj.source.size > TINY
        form = UploadObjectForm(
            data={"title": "Renamed", "author": obj.author}, instance=obj
        )

        assert form.is_valid(), form.errors

    def test_upload_view_does_not_store_an_oversized_object(self):
        User.objects.create_user(username="uploader", password="pw")
        self.client.login(username="uploader", password="pw")
        response = self.client.post(
            reverse("object-upload"),
            {
                "title": "Too big",
                "author": "Test Author",
                "source": upload("big.gif", TINY + 1),
            },
        )

        assert response.status_code == 200
        assert not Object.objects.filter(title="Too big").exists()

    def test_spritesheet_endpoint_rejects_a_gif_over_the_limit(self):
        User.objects.create_user(username="uploader", password="pw")
        self.client.login(username="uploader", password="pw")
        with mock.patch("core.views.views.gif_to_spritesheet") as convert:
            response = self.client.post(
                reverse("convert-spritesheet"),
                {"source": upload("big.gif", TINY + 1, "image/gif")},
            )

        assert response.status_code == 200
        assert "GIF and PNG objects are limited" in response.content.decode()
        convert.assert_not_called()


class TestThumbnailLimits(TestCase):
    def object_form(self, thumbnail):
        return UploadObjectForm(
            data={"title": "Model", "author": "Test Author"},
            files={
                "source": upload("model.glb", 10),
                "thumbnail": SimpleUploadedFile(
                    "thumbnail.png", thumbnail, content_type="image/png"
                ),
            },
        )

    def test_accepts_a_thumbnail_rendered_by_the_upload_page(self):
        form = self.object_form(build_png_bytes(600, 600))

        assert form.is_valid(), form.errors

    @override_settings(MAX_THUMBNAIL_UPLOAD_SIZE=50)
    def test_rejects_a_thumbnail_over_the_size_limit(self):
        form = self.object_form(build_png_bytes(600, 600))

        assert not form.is_valid()
        assert "Thumbnails are limited to 50 B" in form.errors["thumbnail"][0]

    def test_rejects_a_thumbnail_over_the_dimension_limit(self):
        # A flat image compresses to almost nothing, so the byte limit alone
        # would let it through.
        form = self.object_form(
            build_png_bytes(settings.MAX_THUMBNAIL_DIMENSION + 1, 10)
        )

        assert not form.is_valid()
        assert (
            f"{settings.MAX_THUMBNAIL_DIMENSION + 1}x10 pixels"
            in (form.errors["thumbnail"][0])
        )


@override_settings(MAX_AUDIO_UPLOAD_SIZE=TINY)
class TestSoundSizeLimit(TestCase):
    def test_rejects_a_sound_over_the_limit(self):
        form = SoundForm(
            data={"title": "Sound", "author": "Test Author"},
            files={"file": upload("big.wav", TINY + 1)},
        )

        assert not form.is_valid()
        assert "Audio files are limited to 1000 B" in form.errors["file"][0]

    def test_editing_without_replacing_the_file_skips_the_limit(self):
        sound = SoundFactory(file=get_example_sound("happy-message-ping.mp3"))
        assert sound.file.size > TINY
        form = SoundForm(
            data={"title": "Renamed", "author": sound.author}, instance=sound
        )

        assert form.is_valid(), form.errors

    def test_upload_view_does_not_store_an_oversized_sound(self):
        User.objects.create_user(username="uploader", password="pw")
        self.client.login(username="uploader", password="pw")
        response = self.client.post(
            reverse("sound-upload"),
            {
                "title": "Too big",
                "author": "Test Author",
                "file": upload("big.mp3", TINY + 1),
            },
        )

        assert response.status_code == 200
        assert not Sound.objects.filter(title="Too big").exists()


class TestFileHasChanged(TestCase):
    def setUp(self):
        self.sound = SoundFactory(file=ContentFile(b"stored audio", name="a.mp3"))

    def test_same_content_is_unchanged(self):
        new = SimpleUploadedFile("b.mp3", b"stored audio")

        assert not file_has_changed(new, self.sound.file)

    def test_same_size_different_content_is_changed(self):
        new = SimpleUploadedFile("b.mp3", b"stored AUDIO")

        assert file_has_changed(new, self.sound.file)

    def test_different_size_does_not_read_the_stored_file(self):
        new = SimpleUploadedFile("b.mp3", b"a longer stored audio")
        with mock.patch.object(type(self.sound.file), "chunks") as chunks:
            assert file_has_changed(new, self.sound.file)
        chunks.assert_not_called()

    def test_the_stored_file_itself_is_unchanged(self):
        assert not file_has_changed(self.sound.file, self.sound.file)

    def test_files_are_rewound_after_comparing(self):
        new = SimpleUploadedFile("b.mp3", b"stored audio")
        file_has_changed(new, self.sound.file)

        assert new.read() == b"stored audio"
        assert self.sound.file.read() == b"stored audio"
