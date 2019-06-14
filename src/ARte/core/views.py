from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import redirect

from .helpers import handle_upload_image
from .forms import UploadFileForm, ExhibitForm
from .models import Artwork2, Exhibit


def service_worker(request):
    return render(request, 'core/sw.js',
                  content_type='application/x-javascript')

def index(request):
    ctx = {
        "artworks": [
        ]
    }

    return render(request, 'core/exhibit.jinja2', ctx)


def upload_image(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        image = request.FILES.get('file')
        if form.is_valid() and image:
            handle_upload_image(image)
            return HttpResponseRedirect(reverse('index'))
    else:
        form = UploadFileForm()
    return render(request, 'core/upload.jinja2', {'form': form})

def exhibit_select(request):
    if request.method == 'POST':
        form = ExhibitForm(request.POST)
        if form.is_valid():
            exhibit = form.cleaned_data.get('exhibit')
            return redirect("/" + exhibit.slug)
    else:
        form = ExhibitForm()

    return render(request, 'core/exhibit_select.jinja2', {'form':form})
