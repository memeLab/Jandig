from django.test import TestCase
from django.urls import reverse

from blog.models import Post, PostStatus
from blog.views import PAGE_SIZE


class TestBlogIndex(TestCase):
    def test_main_page_shows_all_posts(self):
        """
        Test the main blog page
        """
        # Create sample posts
        for i in range(0, 10):
            Post.objects.create(
                title=f"Test Post {i}",
                body=f"This is the body of test post {i}.",
                status=PostStatus.PUBLISHED,
            )
        response = self.client.get(reverse("blog_index"))

        assert response.status_code == 200
        assert response.context["posts"].count() == PAGE_SIZE
        assert "posts" in response.context
        posts = list(response.context["posts"])

        assert posts[0].title == "Test Post 9"
        assert posts[-1].title == "Test Post 6"
        assert response.context["next_page_number"] == 2
        assert response.context["total_pages"] == 6
        assert response.context["page_url"] == "/memories/"
        assert response.context["blog_categories"].count() > 0

    def test_main_page_with_page_number_negative(self):
        """
        Test the main blog page with a negative page number
        """
        # Create sample posts
        for i in range(0, 10):
            Post.objects.create(
                title=f"Test Post {i}",
                body=f"This is the body of test post {i}.",
                status=PostStatus.PUBLISHED,
            )
        # Request with a negative page number should return the first page
        response = self.client.get(reverse("blog_index"), {"page": -1})

        assert response.status_code == 200
        assert response.context["posts"].count() == PAGE_SIZE
        assert "posts" in response.context
        posts = list(response.context["posts"])
        assert posts[0].title == "Test Post 9"
        assert posts[-1].title == "Test Post 6"
        assert response.context["next_page_number"] == 2
        assert response.context["total_pages"] == 6

    def test_main_page_with_page_invalid_number(self):
        """
        Test the main blog page with an invalid page number
        """
        # Create sample posts
        for i in range(0, 10):
            Post.objects.create(
                title=f"Test Post {i}",
                body=f"This is the body of test post {i}.",
                status=PostStatus.PUBLISHED,
            )
        # Request with an invalid page number should return the first page
        response = self.client.get(reverse("blog_index"), {"page": "invalid"})

        assert response.status_code == 200
        assert response.context["posts"].count() == PAGE_SIZE
        assert "posts" in response.context
        posts = list(response.context["posts"])
        assert posts[0].title == "Test Post 9"
        assert posts[-1].title == "Test Post 6"
        assert response.context["next_page_number"] == 2
        assert response.context["total_pages"] == 6

    def test_main_page_with_htmx(self):
        """
        Test the main blog page with HTMX request
        """
        # Create sample posts
        for i in range(0, 10):
            Post.objects.create(
                title=f"Test Post {i}",
                body=f"This is the body of test post {i}.",
                status=PostStatus.PUBLISHED,
            )
        response = self.client.get(
            reverse("blog_index"), {"page": 2}, HTTP_HX_REQUEST="true"
        )

        assert response.status_code == 200
        assert response.context["posts"].count() == PAGE_SIZE
        assert "posts" in response.context
        posts = list(response.context["posts"])
        assert posts[0].title == "Test Post 5"
        assert posts[-1].title == "Test Post 2"
        assert response.context["next_page_number"] == 3
        assert response.context["total_pages"] == 6
        assert response.context["page_url"] == "/memories/"
        assert response.context["blog_categories"].count() > 0

        response = self.client.get(
            reverse("blog_index"), {"page": 3}, HTTP_HX_REQUEST="true"
        )
        assert response.status_code == 200
        assert "posts" in response.context
        posts = list(response.context["posts"])
        assert posts[0].title == "Test Post 1"
        assert posts[1].title == "Test Post 0"
