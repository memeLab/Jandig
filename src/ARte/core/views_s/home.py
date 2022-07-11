from django.shortcuts import render
from django.http import JsonResponse


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
