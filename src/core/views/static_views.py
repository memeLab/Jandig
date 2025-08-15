from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.templatetags.static import static


def ar_viewer(request):
    return render(request, "core/exhibit.jinja2")


def community(request):
    return render(request, "core/community.jinja2")


def documentation(request):
    return render(request, "core/documentation.jinja2", {})


def favicon(_):
    return redirect(static("images/icons/favicon.ico"))


def health_check(_):
    return JsonResponse({"status": "ok"}, status=200)


def me_hotsite(request, _):
    return render(request, "core/ME/hotsite.html", {})


def home(request):
    return render(request, "core/home.jinja2", {})


def manifest(request):
    return render(
        request, "core/manifest.json", content_type="application/x-javascript"
    )


def marker_generator(request):
    return render(request, "core/generator.html", {})


def robots_txt(_):
    lines = [
        "User-Agent: *",
        "Disallow: ",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def service_worker(request):
    return render(request, "core/sw.js", content_type="application/x-javascript")
