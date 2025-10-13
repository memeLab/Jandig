from django.test import TestCase
from django.urls import reverse

from blog.models import Post, PostImage, PostStatus


class TestPostDetails(TestCase):
    def test_post_details_work(self):
        """
        Test the post detail page
        """
        # Create a sample post
        post = Post.objects.create(
            title="Test Post", body="This is a test post.", status=PostStatus.PUBLISHED
        )
        # Create a sample image for the post
        image_1 = PostImage.objects.create(
            file="test_image.jpg",  # Assuming you have a valid image path
            description="Test Image",
        )
        image_2 = PostImage.objects.create(
            file="test_image_2.jpg",  # Assuming you have a valid image path
            description="Test Image 2",
        )
        post.images.set([image_1, image_2])
        response = self.client.get(reverse("post_detail", args=[post.pk]))

        assert response.status_code == 200
        assert response.context["post"].pk == post.pk
        assert response.context["post"].title == "Test Post"
        assert response.context["images"].count() == 2
        assert response.context["images"].first().description == "Test Image"
        assert response.context["images"].last().description == "Test Image 2"
