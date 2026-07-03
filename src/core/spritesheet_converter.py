"""
GIF to PNG spritesheet conversion.

Converts animated GIF files into indexed PNG spritesheets for efficient
rendering in Three.js AR scenes.
"""

import io
import math

from PIL import Image


def gif_to_spritesheet(gif_file):
    """
    Convert an animated GIF to an indexed PNG spritesheet.

    Args:
        gif_file: A file-like object containing GIF data.

    Returns:
        A tuple of (png_bytes, metadata) where:
        - png_bytes: bytes of the PNG spritesheet
        - metadata: dict with keys: columns, rows, total_frames,
          frame_width, frame_height, frame_durations

    Raises:
        ValueError: If the file is not a valid GIF or has no frames.
    """
    img = Image.open(gif_file)

    if img.format != "GIF":
        raise ValueError("File is not a GIF image.")

    frames = []
    durations = []

    try:
        while True:
            # Convert frame to RGBA to handle transparency and disposal correctly
            frame = img.convert("RGBA")
            frames.append(frame.copy())
            # Duration in milliseconds; default 100ms if not specified
            durations.append(img.info.get("duration", 100))
            img.seek(img.tell() + 1)
    except EOFError:
        pass

    if not frames:
        raise ValueError("GIF has no frames.")

    total_frames = len(frames)
    frame_width, frame_height = frames[0].size

    # Calculate grid dimensions
    columns = math.ceil(math.sqrt(total_frames))
    rows = math.ceil(total_frames / columns)

    # Create the spritesheet canvas (RGBA)
    sheet_width = columns * frame_width
    sheet_height = rows * frame_height
    spritesheet = Image.new("RGBA", (sheet_width, sheet_height), (0, 0, 0, 0))

    # Paste frames into grid
    for i, frame in enumerate(frames):
        col = i % columns
        row = i // columns
        x = col * frame_width
        y = row * frame_height
        spritesheet.paste(frame, (x, y))

    # Quantize to 255 colors, reserving index 0 for transparency
    # RGBA images require FASTOCTREE method in Pillow
    quantized = spritesheet.quantize(colors=255, method=Image.Quantize.FASTOCTREE)

    # Save as PNG
    output = io.BytesIO()
    quantized.save(output, format="PNG", optimize=True)
    png_bytes = output.getvalue()

    # Use the most common duration as the single frameDurationMs
    frame_duration_ms = max(set(durations), key=durations.count)

    metadata = {
        "frames": total_frames,
        "frameWidth": frame_width,
        "frameHeight": frame_height,
        "columns": columns,
        "rows": rows,
        "sheetWidth": sheet_width,
        "sheetHeight": sheet_height,
        "frameDurationMs": frame_duration_ms,
    }

    return png_bytes, metadata
