"""Tests for GIF to PNG spritesheet conversion."""

import io
import math

from PIL import Image

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from src.core.spritesheet_converter import gif_to_spritesheet
from users.models import Profile, User

GUEIXA_GIF_PATH = "collection/objects/gueixa.gif"


def _make_gif(frames_count=4, frame_size=(10, 10), durations=None, transparent=False):
    """Helper to create an in-memory GIF with the given number of frames."""
    if durations is None:
        durations = [100] * frames_count

    frames = []
    for i in range(frames_count):
        if transparent:
            frame = Image.new("RGBA", frame_size, (0, 0, 0, 0))
            # Draw something visible in part of the frame
            pixels = frame.load()
            for x in range(frame_size[0] // 2):
                for y in range(frame_size[1] // 2):
                    pixels[x, y] = (255, 0, i * 20, 255)
        else:
            # Use different colors per frame to verify they are distinct
            color = ((i * 50) % 256, (i * 80) % 256, (i * 110) % 256)
            frame = Image.new("RGB", frame_size, color)
        frames.append(frame)

    output = io.BytesIO()
    if transparent:
        frames[0].save(
            output,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0,
            transparency=0,
            disposal=2,
        )
    else:
        frames[0].save(
            output,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0,
        )
    output.seek(0)
    return output


class TestGifToSpritesheet(TestCase):
    """Unit tests for the gif_to_spritesheet conversion function."""

    def test_basic_conversion_dimensions_and_metadata(self):
        """Test basic conversion produces correct grid dimensions and metadata."""
        gif_file = _make_gif(frames_count=9, frame_size=(20, 20))
        png_bytes, metadata = gif_to_spritesheet(gif_file)

        assert metadata["frames"] == 9
        assert metadata["frameWidth"] == 20
        assert metadata["frameHeight"] == 20
        # ceil(sqrt(9)) = 3
        assert metadata["columns"] == 3
        assert metadata["rows"] == 3
        assert metadata["sheetWidth"] == 60
        assert metadata["sheetHeight"] == 60
        assert metadata["frameDurationMs"] == 100

        # Verify output is a valid PNG
        img = Image.open(io.BytesIO(png_bytes))
        assert img.format == "PNG"
        assert img.size == (60, 60)  # 3*20 x 3*20

    def test_conversion_with_gueixa_gif(self):
        """Test conversion with a real GIF file from the collection."""
        with open(GUEIXA_GIF_PATH, "rb") as f:
            png_bytes, metadata = gif_to_spritesheet(f)

        assert metadata["frames"] > 1
        assert metadata["frameWidth"] > 0
        assert metadata["frameHeight"] > 0
        assert metadata["columns"] == math.ceil(math.sqrt(metadata["frames"]))
        assert metadata["rows"] == math.ceil(
            metadata["frames"] / metadata["columns"]
        )
        assert metadata["sheetWidth"] == metadata["columns"] * metadata["frameWidth"]
        assert metadata["sheetHeight"] == metadata["rows"] * metadata["frameHeight"]
        assert isinstance(metadata["frameDurationMs"], int)

        # Verify output PNG dimensions match grid
        img = Image.open(io.BytesIO(png_bytes))
        assert img.size == (metadata["sheetWidth"], metadata["sheetHeight"])

    def test_transparency_preserved(self):
        """Test that transparency is preserved in the spritesheet."""
        gif_file = _make_gif(frames_count=4, frame_size=(10, 10), transparent=True)
        png_bytes, metadata = gif_to_spritesheet(gif_file)

        img = Image.open(io.BytesIO(png_bytes))
        # PNG should have transparency info
        assert img.info.get("transparency") is not None or img.mode == "P"

    def test_variable_durations(self):
        """Test that the most common frame duration is used."""
        durations = [50, 100, 100, 100]
        gif_file = _make_gif(frames_count=4, frame_size=(10, 10), durations=durations)
        _, metadata = gif_to_spritesheet(gif_file)

        assert metadata["frameDurationMs"] == 100

    def test_single_frame_gif(self):
        """Test conversion of a single-frame GIF."""
        gif_file = _make_gif(frames_count=1, frame_size=(32, 32))
        png_bytes, metadata = gif_to_spritesheet(gif_file)

        assert metadata["frames"] == 1
        assert metadata["columns"] == 1
        assert metadata["rows"] == 1
        assert metadata["frameWidth"] == 32
        assert metadata["frameHeight"] == 32
        assert metadata["sheetWidth"] == 32
        assert metadata["sheetHeight"] == 32

        img = Image.open(io.BytesIO(png_bytes))
        assert img.size == (32, 32)

    def test_many_frames_gif(self):
        """Test conversion of a GIF with many frames (100+)."""
        gif_file = _make_gif(frames_count=120, frame_size=(8, 8))
        png_bytes, metadata = gif_to_spritesheet(gif_file)

        assert metadata["frames"] == 120
        # ceil(sqrt(120)) = 11
        assert metadata["columns"] == 11
        assert metadata["rows"] == math.ceil(120 / 11)
        assert metadata["sheetWidth"] == 11 * 8
        assert metadata["sheetHeight"] == metadata["rows"] * 8

        img = Image.open(io.BytesIO(png_bytes))
        assert img.size == (metadata["sheetWidth"], metadata["sheetHeight"])

    def test_non_gif_file_rejected(self):
        """Test that non-GIF files raise ValueError."""
        # Create a PNG file
        png_file = io.BytesIO()
        Image.new("RGB", (10, 10), (255, 0, 0)).save(png_file, format="PNG")
        png_file.seek(0)

        with self.assertRaises(ValueError) as ctx:
            gif_to_spritesheet(png_file)
        assert "not a GIF" in str(ctx.exception)

    def test_non_image_file_rejected(self):
        """Test that non-image files raise an error."""
        fake_file = io.BytesIO(b"not an image at all")
        fake_file.seek(0)

        with self.assertRaises(Exception):
            gif_to_spritesheet(fake_file)


class TestConvertSpritesheetEndpoint(TestCase):
    """Tests for the HTMX spritesheet conversion endpoint."""

    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )
        self.profile = Profile.objects.get(user=self.user)
        self.url = reverse("convert-spritesheet")

    def test_unauthenticated_redirects(self):
        gif_file = _make_gif(frames_count=4, frame_size=(10, 10))
        response = self.client.post(
            self.url,
            {"source": SimpleUploadedFile("test.gif", gif_file.read(), content_type="image/gif")},
        )
        assert response.status_code == 302
        assert "/users/login" in response.url

    def test_gif_conversion_returns_hidden_inputs(self):
        self.client.login(username=self.username, password=self.password)
        gif_file = _make_gif(frames_count=4, frame_size=(10, 10))
        response = self.client.post(
            self.url,
            {"source": SimpleUploadedFile("test.gif", gif_file.read(), content_type="image/gif")},
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert 'name="spritesheet_path"' in content
        assert 'name="spritesheet_metadata_path"' in content

    def test_non_gif_returns_empty(self):
        self.client.login(username=self.username, password=self.password)
        png_buf = io.BytesIO()
        Image.new("RGB", (10, 10)).save(png_buf, format="PNG")
        png_buf.seek(0)
        response = self.client.post(
            self.url,
            {"source": SimpleUploadedFile("test.png", png_buf.read(), content_type="image/png")},
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert 'name="spritesheet_path"' not in content
        assert "error" not in content.lower() or "not_gif" in content.lower()

    def test_no_file_returns_error(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(self.url, {})
        assert response.status_code == 200
        content = response.content.decode()
        assert "No file provided" in content or "error" in content.lower()
