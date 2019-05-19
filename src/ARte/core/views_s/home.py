from django.shortcuts import render, Http404
from django.urls import reverse


def home(request):
    markers = 1
    objects = 1
    exhibits = 1

    return render(request, 'core/home.jinja2', 
    {'markers': markers, 'objects': objects, 'exhibits': exhibits})


def ar_viewer(request):
    return render(request, 'core/exhibit.jinja2')


def docs(request):
    raise Http404

def community(request):
    raise Http404