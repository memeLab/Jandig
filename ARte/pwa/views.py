from django.shortcuts import render
from .models import Marker

def service_worker(request):
    return render(request, 'pwa/sw.js',
                  content_type='application/x-javascript')


def index(request):
    ctx = {"markers":[
                Marker(patt="gueixa", gif="gueixa"),
                Marker(patt="temaki", gif="temaki"),
                Marker(patt="robo-rodas", gif="robo-rodas", scale="1 1.5"),
                Marker(patt="tokusatsu", gif="tokusatsu"),
                Marker(patt="samurai", gif="samurai", scale="1.5 1.5"),
                Marker(patt="antipodas", gif="antipodas"), # Blinking

                # Marker(patt="hiro", gif="none"),
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
