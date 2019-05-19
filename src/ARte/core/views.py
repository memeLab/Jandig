from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .helpers import handle_upload_image
from .forms import UploadFileForm
from .models import Artwork2


def service_worker(request):
    return render(request, 'core/sw.js',
                  content_type='application/x-javascript')

def index(request):
    ctx = {
        "artworks": [
            Artwork2(patt="antipodas", gif="antipodas", scale="1.5 1.5"),
            Artwork2(patt="gueixa", gif="gueixa"),
            Artwork2(patt="manekineko", gif="manekineko"),
            Artwork2(patt="pedrinhazinha", gif="pedrinhazinha"),
            Artwork2(patt="peixe", gif="peixe"),
            Artwork2(patt="flyingsaucer", gif="flyingsaucer", scale="1.5 1"),
            # Artwork(patt="robo3dandando", gif="robo3dandando"),
            # Artwork(patt="robo3dvoando", gif="robo3dvoando"),
            Artwork2(patt="andando", gif="andando"),
            Artwork2(patt="robo-pula", gif="robo-pula"),
            Artwork2(patt="robo-rodas", gif="robo-rodas"),
            # Artwo2rk(patt="robos", gif="robos"), # it seems that the files are not here
            Artwork2(patt="samurai", gif="samurai", scale="1.5 1.5"),
            Artwork2(patt="binoculos", gif="janela"),
            Artwork2(patt="temaki", gif="temaki"),
            Artwork2(patt="tokusatsu", gif="tokusatsu"),
            Artwork2(patt="catavento", gif="catavento", scale="1.5 1.5"),
            Artwork2(patt="hamsa", gif="hamsa", scale="1.5 1.5"), 
            Artwork2(patt="pattern-hiro", gif="tokusatsu-test"),

	    # disabled
            # Artwork(patt="saucer", gif="saucer"),
            # Artwork(patt="binoculos", gif="janela"),
            # Artwork(patt="gueixa2", gif="gueixa2"),
    	    # Artwork(patt="jandig-marker", gif="moonwalker"),
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
