from django.shortcuts import render, Http404
from django.urls import reverse


def home(request):
    exhibits = 0
    return render(request, 'users/profile.jinja2',
    {'exhibits': exhibits})


def ar_viewer(request):
    return render(request, 'core/exhibit.jinja2')


def docs(request):
    raise Http404

def community(request):
    raise Http404