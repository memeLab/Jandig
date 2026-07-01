from io import BytesIO

from PIL import Image

from core.media_dimensions import extract_dimensions


def _make_png(width, height):
    """Create a minimal PNG in memory."""
    img = Image.new("RGBA", (width, height), (255, 0, 0, 255))
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def _make_gif(width, height, frames=2):
    """Create a minimal GIF in memory."""
    imgs = [
        Image.new("RGBA", (width, height), (i * 50, 100, 100, 255))
        for i in range(frames)
    ]
    buf = BytesIO()
    imgs[0].save(buf, format="GIF", save_all=True, append_images=imgs[1:], duration=100)
    buf.seek(0)
    return buf


def _make_mp4(width, height):
    """Create a minimal MP4 video in memory using PyAV."""
    import av

    buf = BytesIO()
    container = av.open(buf, mode="w", format="mp4")
    stream = container.add_stream("h264", rate=1)
    stream.width = width
    stream.height = height
    stream.pix_fmt = "yuv420p"

    frame = av.VideoFrame.from_ndarray(
        __import__("numpy").zeros((height, width, 3), dtype="uint8"), format="rgb24"
    )
    for packet in stream.encode(frame):
        container.mux(packet)
    for packet in stream.encode():
        container.mux(packet)
    container.close()
    buf.seek(0)
    return buf


class TestExtractDimensionsPNG:
    def test_png_dimensions(self):
        buf = _make_png(800, 600)
        result = extract_dimensions(buf, "png")
        assert result == (800, 600)

    def test_png_square(self):
        buf = _make_png(256, 256)
        result = extract_dimensions(buf, "png")
        assert result == (256, 256)


class TestExtractDimensionsGIF:
    def test_gif_dimensions(self):
        buf = _make_gif(320, 240)
        result = extract_dimensions(buf, "gif")
        assert result == (320, 240)

    def test_gif_wide(self):
        buf = _make_gif(1920, 1080)
        result = extract_dimensions(buf, "gif")
        assert result == (1920, 1080)


class TestExtractDimensionsVideo:
    def test_mp4_dimensions(self):
        buf = _make_mp4(640, 480)
        result = extract_dimensions(buf, "mp4")
        assert result == (640, 480)

    def test_webm_extension_dispatches_to_video(self):
        # webm uses the same code path as mp4
        buf = _make_mp4(1280, 720)
        result = extract_dimensions(buf, "webm")
        assert result == (1280, 720)


class TestExtractDimensionsGLB:
    def test_glb_with_thumbnail(self):
        thumb = _make_png(512, 384)
        buf = BytesIO(b"fake glb content")
        result = extract_dimensions(buf, "glb", thumbnail=thumb)
        assert result == (512, 384)

    def test_glb_without_thumbnail(self):
        buf = BytesIO(b"fake glb content")
        result = extract_dimensions(buf, "glb", thumbnail=None)
        assert result is None


class TestExtractDimensionsEdgeCases:
    def test_corrupt_file_returns_none(self):
        buf = BytesIO(b"this is not a valid image")
        result = extract_dimensions(buf, "png")
        assert result is None

    def test_unknown_extension_returns_none(self):
        buf = BytesIO(b"something")
        result = extract_dimensions(buf, "xyz")
        assert result is None

    def test_file_position_restored_after_image(self):
        buf = _make_png(100, 100)
        buf.seek(5)
        extract_dimensions(buf, "png")
        assert buf.tell() == 5

    def test_file_position_restored_after_video(self):
        buf = _make_mp4(320, 240)
        buf.seek(0)
        extract_dimensions(buf, "mp4")
        assert buf.tell() == 0
