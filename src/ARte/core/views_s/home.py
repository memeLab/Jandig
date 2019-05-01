from django.shortcuts import render
from django.urls import reverse


def home(request):
    return render(request, 'core/home.jinja2')