"""Guard the escaping of user-supplied text rendered through fast_html.

`fast_html` escapes nothing, and the modal templates render its output with
`| safe`, so anything reaching an attribute unescaped is a stored XSS. See #888.
"""

from django.test import TestCase

from core.tests.factory import MarkerFactory, ObjectFactory, SoundFactory

BREAKOUT = '" onerror="alert(1)'


class TestFastHtmlEscaping(TestCase):
    def test_fast_html_still_does_not_escape(self):
        """If this ever fails, fast_html started escaping and the call-site
        escaping below could be reconsidered. Until then it is load-bearing."""
        from fast_html import img, render

        assert render(img(src="x", title=BREAKOUT)) == (
            f'<img src="x" title="{BREAKOUT}">'
        )

    def test_a_marker_title_cannot_break_out_of_the_attribute(self):
        marker = MarkerFactory(title=BREAKOUT)

        html = marker.as_html()

        assert 'onerror="alert(1)"' not in html
        assert "&quot;" in html or "&#34;" in html, html

    def test_an_object_title_cannot_break_out_of_the_attribute(self):
        obj = ObjectFactory(title=BREAKOUT)

        html = obj.as_html()

        assert 'onerror="alert(1)"' not in html

    def test_a_sound_title_cannot_break_out_of_the_attribute(self):
        sound = SoundFactory(title=BREAKOUT)

        html = sound.as_html()

        assert 'onerror="alert(1)"' not in html

    def test_a_script_tag_in_a_title_is_neutralised(self):
        marker = MarkerFactory(title="<script>alert(1)</script>")

        html = marker.as_html()

        assert "<script>" not in html
