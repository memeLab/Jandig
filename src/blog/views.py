from django.shortcuts import render

from blog.models import Category, Clipping, Post, PostStatus

PREVIEW_SIZE = 300
PAGE_SIZE = 4


def blog_index(request):
    actual_page_number = int(request.GET.get("page", "1"))
    initial_post = 0 + (actual_page_number - 1) * PAGE_SIZE
    last_post = PAGE_SIZE * actual_page_number
    posts = (
        Post.objects.prefetch_related("categories")
        .filter(status=PostStatus.PUBLISHED)
        .all()
        .order_by("-created")[initial_post:last_post]
    )

    context = {
        "next_page_number": actual_page_number + 1,
        "posts": posts,
        "PREVIEW_SIZE": PREVIEW_SIZE,
        "page_size": PAGE_SIZE,
        "page_url": "/memories/",
        "blog_categories": Category.objects.all(),
    }
    if request.htmx:
        return render(request, "blog/post_preview.jinja2", context)

    return render(request, "blog/index.jinja2", context)


def blog_category(request, category):
    actual_page_number = int(request.GET.get("page", "1"))
    initial_post = 0 + (actual_page_number - 1) * PAGE_SIZE
    last_post = PAGE_SIZE * actual_page_number
    posts = (
        Post.objects.prefetch_related("categories")
        .filter(categories__name__contains=category)
        .order_by("-created")[initial_post:last_post]
    )

    context = {
        "next_page_number": actual_page_number + 1,
        "category": category,
        "posts": posts,
        "PREVIEW_SIZE": PREVIEW_SIZE,
        "page_size": PAGE_SIZE,
        "page_url": request.path,
        "blog_categories": Category.objects.all(),
    }

    if request.htmx:
        return render(request, "blog/post_preview.jinja2", context)

    return render(request, "blog/category.jinja2", context)


def blog_detail(request, pk):
    post = Post.objects.prefetch_related("images", "categories").get(pk=pk)

    context = {"post": post, "images": post.images.all()}

    return render(request, "blog/detail.jinja2", context)


def clipping(request):
    clippings = Clipping.objects.all().order_by("-created")
    context = {"clippings": clippings}
    return render(request, "blog/clipping.jinja2", context)
