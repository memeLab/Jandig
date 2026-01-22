from django.core.paginator import Paginator
from django.shortcuts import render

from blog.models import Category, Clipping, Post, PostStatus

PREVIEW_SIZE = 300
PAGE_SIZE = 4


def blog_index(request):
    try:
        page_number = int(request.GET.get("page", "1"))
    except ValueError:
        page_number = 1
    paginator = Paginator(
        Post.objects.prefetch_related("categories")
        .filter(status=PostStatus.PUBLISHED)
        .order_by("-created"),
        PAGE_SIZE,
    )
    if page_number < 1:
        page_number = 1

    page = paginator.get_page(page_number)
    posts = page.object_list

    context = {
        "next_page_number": page_number + 1,
        "posts": posts,
        "PREVIEW_SIZE": PREVIEW_SIZE,
        "last_page": page.has_previous(),
        "total_pages": paginator.num_pages,
        "page_url": "/memories/",
        "blog_categories": Category.objects.all(),
    }
    if request.htmx:
        return render(request, "blog/post_preview.jinja2", context)

    return render(request, "blog/index.jinja2", context)


def post_detail(request, pk):
    post = Post.objects.prefetch_related("images", "categories").get(pk=pk)

    context = {"post": post, "images": post.images.all()}

    return render(request, "blog/detail.jinja2", context)


def clipping(request):
    clippings = Clipping.objects.all().order_by("-display_date")
    context = {"clippings": clippings}
    return render(request, "blog/clipping.jinja2", context)
