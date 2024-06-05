from django.shortcuts import render

from blog.models import Post, PostStatus

PREVIEW_SIZE=300
def blog_index(request):

    posts = Post.objects.filter(status=PostStatus.PUBLISHED).all().order_by("-created")
    context = {
        "posts": posts,
        "PREVIEW_SIZE": PREVIEW_SIZE,
    }
    return render(request, "blog/index.jinja2", context)

def blog_category(request, category):

    posts = Post.objects.filter(
        categories__name__contains=category
    ).order_by("-created")

    context = {
        "category": category,
        "posts": posts,
        "PREVIEW_SIZE": PREVIEW_SIZE,
    }

    return render(request, "blog/category.jinja2", context)

def blog_detail(request, pk):

    post = Post.objects.get(pk=pk)

    context = {
        "post": post,
    }

    return render(request, "blog/detail.jinja2", context)