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
                excerpt=f"This is the excerpt of test post {i}.",
                formatted_body=f"This is the body of test post {i}.",
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
                excerpt=f"This is the excerpt of test post {i}.",
                formatted_body=f"This is the body of test post {i}.",
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
                excerpt=f"This is the excerpt of test post {i}.",
                formatted_body=f"This is the body of test post {i}.",
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
                excerpt=f"This is the excerpt of test post {i}.",
                formatted_body=f"This is the body of test post {i}.",
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

    def test_last_page_flag_is_true_only_on_the_final_page(self):
        """
        `last_page` must report whether the current page is the final one.

        It used to be set from `page.has_previous()`, which is the inverse:
        False on page 1 and True on every other page.
        """
        for i in range(10):
            Post.objects.create(
                title=f"Test Post {i}",
                excerpt=f"This is the excerpt of test post {i}.",
                formatted_body=f"This is the body of test post {i}.",
                status=PostStatus.PUBLISHED,
            )

        first = self.client.get(reverse("blog_index"))
        total_pages = first.context["total_pages"]
        assert total_pages > 2, "this test needs at least three pages to be meaningful"
        assert first.context["last_page"] is False

        middle = self.client.get(reverse("blog_index"), {"page": total_pages - 1})
        assert middle.context["last_page"] is False

        last = self.client.get(reverse("blog_index"), {"page": total_pages})
        assert last.context["last_page"] is True

    def test_last_page_flag_is_true_when_all_posts_fit_in_one_page(self):
        """A single page of results is also the last page."""
        Post.objects.all().delete()
        Post.objects.create(
            title="Only Post",
            excerpt="Excerpt.",
            formatted_body="Body.",
            status=PostStatus.PUBLISHED,
        )
        response = self.client.get(reverse("blog_index"))

        assert response.context["total_pages"] == 1
        assert response.context["last_page"] is True
