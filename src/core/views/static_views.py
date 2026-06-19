from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.templatetags.static import static


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


def home_new(request):
    return render(request, "core/home_v2.jinja2", {})


def home_old(request):
    return render(request, "core/home.jinja2", {})


def manifest(request):
    return render(
        request, "core/manifest.json", content_type="application/x-javascript"
    )


def marker_generator(request):
    return render(request, "core/generator.html", {})


def robots_txt(request):
    # Block bots entirely on dev/staging hosts so dev.jandig.app stops
    # showing up in search results.
    host = request.get_host().lower()
    if host.startswith("dev.") or "staging" in host:
        lines = ["User-Agent: *", "Disallow: /"]
        return HttpResponse("\n".join(lines), content_type="text/plain")

    # Production: allow only the public CMS/blog surface. Block API,
    # exhibit detail pages (bots feed random ids and cause 500s), and
    # auth-gated CMS edit/upload paths.
    lines = [
        "User-Agent: *",
        "Allow: /$",
        "Allow: /collection/",
        "Allow: /community/",
        "Allow: /documentation/",
        "Allow: /memories/",
        "Allow: /docs/",
        "Allow: /see_all/",
        "Disallow: /api/",
        "Disallow: /admin/",
        "Disallow: /users/",
        "Disallow: /exhibit/",
        "Disallow: /exhibits/",
        "Disallow: /artwork/",
        "Disallow: /artworks/",
        "Disallow: /marker/",
        "Disallow: /markers/",
        "Disallow: /objects/",
        "Disallow: /sounds/",
        "Disallow: /generator/",
        "Disallow: /content/delete/",
        "Disallow: /elements/",
        "Disallow: /exhibit_select/",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def service_worker(request):
    return render(request, "core/sw.js", content_type="application/x-javascript")
