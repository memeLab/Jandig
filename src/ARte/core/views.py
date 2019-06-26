from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import translation
from django.shortcuts import redirect

from .helpers import handle_upload_image
from .forms import UploadFileForm, ExhibitForm
from .models import Artwork2, Exhibit
from users.models import Artwork, Marker, Object


def service_worker(request):
    return render(request, 'core/sw.js',
                  content_type='application/x-javascript')

def index(request):
    ctx = {
        "artworks": [
        ]
    }

    return render(request, 'core/exhibit.jinja2', ctx)

def collection(request):
    ctx = {
        "artworks": Artwork.objects.all(),
        "exhibits": Exhibit.objects.all(),
        "markers": Marker.objects.all(),
        "objects": Object.objects.all(),
    }

    return render(request, 'core/collection.jinja2', ctx)

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

def exhibit_detail(request):
    id = request.GET.get("id")
    exhibit = Exhibit.objects.get(id=id)
    ctx = {
        'exhibit':exhibit,
        'exhibitImage': "https://cdn3.iconfinder.com/data/icons/basic-mobile-part-2/512/painter-512.png",
        'artworks': exhibit.artworks.all()
    }
    return render(request, 'core/exhibit_detail.jinja2', ctx)


def lang_selector(request):
    user_language = request.POST.get('language', '')
    response = redirect('home')
    if user_language:
        print('old ' + translation.get_language())
        translation.activate(user_language)
        print('new ' + translation.get_language())
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user_language)
        
    return response