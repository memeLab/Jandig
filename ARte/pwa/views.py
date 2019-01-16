from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .helpers import handle_upload_image
from .forms import UploadFileForm
from .models import Artwork


def service_worker(request):
    return render(request, 'pwa/sw.js',
                  content_type='application/x-javascript')


def index(request):
    ctx = {
        "artworks": [
            # Artwork(patt="hiro"),
            # Artwork(patt="gueixa", gif="gueixa"),
            Artwork(patt="temaki", gif="temaki"),
            # Artwork(patt="robo-rodas", gif="robo-rodas", scale="1 1.5"),
            # Artwork(patt="tokusatsu", gif="tokusatsu"),
            # Artwork(patt="samurai", gif="samurai", scale="1.5 1.5"),
            # Artwork(patt="antipodas", gif="antipodas"),
            # Artwork(patt="flyingsaucer", gif="flyingsaucer", scale="1.5 1"),
            # Artwork(patt="manekineko", gif="manekineko"),

            # Artwork(patt="peixe", gif="peixe"),
            # Artwork(patt="andando", gif="andando"),
            # Artwork(patt="robo-pula", gif="robo-pula"),
            # Artwork(patt="robo3dandando", gif="robo3dandando"),
            # Artwork(patt="robo3dvoando", gif="robo3dvoando"),
            # Artwork(patt="saucer", gif="saucer"),
            # Artwork(patt="flyingsaucer", gif="flyingsaucer"),
            # Artwork(patt="robo-rodas", gif="robo-rodas"),
            # Artwork(patt="janela", gif="janela"),
            # Artwork(patt="binoculos", gif="janela"),
            # Artwork(patt="gueixa2", gif="gueixa2"),
            # Artwork(patt="iemanja", gif="iemanja"),
            # Artwork(patt="pedrinhazinha", gif="pedinhazinha"),
        ]
    }

    return render(request, 'pwa/exhibit.jinja2', ctx)


def upload_image(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        image = request.FILES.get('file')
        if form.is_valid() and image:
            handle_upload_image(image)
            return HttpResponseRedirect(reverse('index'))
    else:
        form = UploadFileForm()
    return render(request, 'pwa/upload.jinja2', {'form': form})
