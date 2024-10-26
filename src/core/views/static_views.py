from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from django.templatetags.static import static

def home(request):
    return render(request, "users/profile.jinja2", {})


def documentation(request):
    return render(request, "core/documentation.jinja2", {})


def ar_viewer(request):
    return render(request, "core/exhibit.jinja2")


def community(request):
    return render(request, "core/community.jinja2")


def marker_generator(request):
    return render(request, "core/generator.html", {})


def health_check(request):
    return JsonResponse({"status": "ok"}, status=200)


def favicon(request):
    return redirect(static("images/icons/favicon.ico"))


def robots_txt(request):
    lines = [
        "User-Agent: *",
        "Disallow: ",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")