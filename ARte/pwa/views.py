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
        "artworks":[
            Artwork(patt="gueixa", gif="gueixa"),
            Artwork(patt="temaki", gif="temaki"),
            Artwork(patt="robo-rodas", gif="robo-rodas", scale="1 1.5"),
            Artwork(patt="tokusatsu", gif="tokusatsu"),
            Artwork(patt="samurai", gif="samurai", scale="1.5 1.5"),
            Artwork(patt="antipodas", gif="antipodas"), # Blinking
            Artwork(patt="flyingsaucer", gif="flyingsaucer", scale="1.5 1"), # Blinking
            Artwork(patt="manekineko", gif="manekineko"),

                # Artwork(patt="hiro", gif="none"),
                # {"patt":"peixe", "image":"peixe"},
                # {"patt":"andando", "image":"andando"},
                # {"patt":"robo-pula", "image":"robo-pula"},
                # {"patt":"robo3dandando", "image":"robo3dandando"},
                # {"patt":"robo3dvoando", "image":"robo3dvoando"},
                # {"patt":"saucer", "image":"saucer"},
                # {"patt":"flyingsaucer", "image":"andando"},
                # {"patt":"manekineko", "image":"robo-rodas"},

                # {"patt":"janela", "image":"janela"}, # Gif bugging
                    # {"patt":"binoculos", "image":"janela"}, Not Working
                    # {"patt":"gueixa2", "image":"gueixa2"}, Not Working
                    # {"patt":"iemanja", "image":"iemanja"}, Not Working
                    # {"patt":"pedrinhazinha", "image":"pedrinhazinha"}, Not Working
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
