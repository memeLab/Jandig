from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.templatetags.static import static
from django.views.static import serve as static_serve


def community(request):
    return render(request, "core/community.jinja2")


def documentation(request):
    return render(request, "core/documentation.jinja2", {})


def favicon(_):
    return redirect(static("images/icons/favicon.ico"))


def health_check(_):
    return JsonResponse({"status": "ok"}, status=200)


def me_hotsite(request):
    return render(request, "core/ME/hotsite.html", {})


def home(request):
    return render(request, "core/home.jinja2", {})


def manifest(request):
    agent = request.META.get("HTTP_USER_AGENT", "")
    if any(
        device in agent.lower()
        for device in ["ipad", "iphone", "mac", "safari", "ios", "apple"]
    ):
        return redirect(static("files/ios-manifest.json"))
    return redirect(static("files/manifest.json"))


def marker_generator(request):
    return render(request, "core/generator.html", {})


def robots_txt(_):
    lines = [
        "User-Agent: *",
        "Disallow: ",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def service_worker(request):
    return redirect(static("js/sw.js"))


def serve_docs(request, path):
    if not path or path.endswith("/"):
        path += "index.html"
    return static_serve(request, path, document_root=settings.DOCS_ROOT)
