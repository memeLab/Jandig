"""
QR codes that send visitors to an exhibit or artwork (#810), so artists don't
need an external generator to print or show them.

The codes are built on every request from the public URL and never stored.
"""

import io

import segno
from django.urls import reverse
from markupsafe import Markup

# 4px per module keeps the inline code around 150px wide, easy to scan from a
# desktop screen; downloads use 10px per module so they print sharply.
INLINE_SCALE = 4
DOWNLOAD_SCALE = 10
# White background, so the code stays scannable on the patterned page and on
# coloured paper (segno's SVG default is transparent).
LIGHT = "#fff"

CONTENT_TYPES = {"svg": "image/svg+xml", "png": "image/png"}


def public_url(request, path):
    # SSL terminates at the load balancer, so request.scheme is "http" even in
    # production; public links are always https (#822).
    return f"https://{request.get_host()}{path}"


def exhibit_url(request, exhibit):
    return public_url(request, reverse("exhibit", kwargs={"slug": exhibit.slug}))


def artwork_url(request, artwork):
    return public_url(request, f"{reverse('artwork-preview')}?id={artwork.id}")


def make(url):
    return segno.make(url, micro=False)


def inline_svg(url):
    """Return the QR code for `url` as SVG markup to embed in a page."""
    return Markup(make(url).svg_inline(scale=INLINE_SCALE, light=LIGHT))


def render(url, file_format):
    """Return the QR code for `url` as a standalone `svg` or `png` file."""
    buffer = io.BytesIO()
    make(url).save(buffer, kind=file_format, scale=DOWNLOAD_SCALE, light=LIGHT)
    return buffer.getvalue()
