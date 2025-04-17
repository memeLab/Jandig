from django.test import TestCase
from django.urls import reverse

from core.tests.factory import MarkerFactory, ObjectFactory, ArtworkFactory, ExhibitFactory
from core.models import DEFAULT_OBJECT_THUMBNAIL_HEIGHT, DEFAULT_OBJECT_THUMBNAIL_WIDTH

class TestMarkerThumbnailGenerators(TestCase):
    def test_thumbnail_generator(self):
        # This is a placeholder for the actual test
        self.assertTrue(True)

class TestObjectThumbnailGenerators(TestCase):
    def setUp(self):
        self.image_object = ObjectFactory(
            title="Test Image",
            source="objects/test.gif",
            scale="2 1",
            position="0 1 0"
        )
        self.video_object = ObjectFactory(
            title="Test Video",
            source="objects/test.mp4",
            scale="1 1",
            position="1 0 0"
        )

    def test_gif_object_as_html_is_image(self):
        html = self.image_object.as_html(height=100, width=200)
        assert f'height="100"' in html
        assert f'width="200"' in html
        assert f'id="{self.image_object.id}"' in html
        assert f'title="{self.image_object.title}"' in html
        assert 'class="trigger-modal"' in html
        assert 'data-elem-type="object"' in html
        assert self.image_object.source.url in html
        assert '<img' in html

    def test_video_object_as_html_is_video(self):
        html = self.video_object.as_html(height=100, width=200)
        assert f'height="100"' in html
        assert f'width="200"' in html
        assert f'id="{self.video_object.id}"' in html
        assert 'autoplay' in html
        assert 'loop' in html
        assert 'data-elem-type="object"' in html
        assert 'class="trigger-modal"' in html
        assert 'muted' in html
        assert '<video' in html

    def test_object_thumbnail_follows_proportion(self):
        html = self.image_object.as_html_thumbnail(editable=False)
        expected_height = DEFAULT_OBJECT_THUMBNAIL_HEIGHT * self.image_object.yproportion
        expected_width = DEFAULT_OBJECT_THUMBNAIL_WIDTH * self.image_object.xproportion
        
        assert f'height="{expected_height}"' in html
        assert f'width="{expected_width}"' in html
        assert 'href="/edit-object' not in html
        assert 'href="/delete-content' not in html

    def test_object_thumbnail_can_be_edited(self):
        html = self.image_object.as_html_thumbnail(editable=True)
        
        edit_url = reverse('edit-object', query={'id': self.image_object.id})
        delete_url = reverse('delete-content', 
                           query={'content_type': 'object', 
                                 'id': self.image_object.id})
        
        assert f'href="{edit_url}"' in html
        assert f'href="{delete_url}"' in html

    def test_object_in_use_cant_be_edited(self):
        # Create an artwork using this object to mark it as "in use"
        ArtworkFactory(augmented=self.image_object)
        
        html = self.image_object.as_html_thumbnail(editable=True)
        assert reverse('edit-object') not in html
        assert reverse('delete-content') not in html

class TestArtworkThumbnailGenerators(TestCase):
    def test_thumbnail_generator(self):
        # This is a placeholder for the actual test
        self.assertTrue(True)

class TestExhibitThumbnailGenerators(TestCase):
    def test_thumbnail_generator(self):
        # This is a placeholder for the actual test
        self.assertTrue(True)
