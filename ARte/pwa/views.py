from django.shortcuts import render


def index(request):
    ctx = {"markers":[
                {"preset":"hiro", "image":"none"},
                {"patt":"peixe", "image":"peixe"}, 
                {"patt":"andando", "image":"andando"}, 
                {"patt":"robo-pula", "image":"robo-pula"},
                {"patt":"robo-rodas", "image":"robo-rodas"}, 
                {"patt":"robo3dandando", "image":"robo3dandando"}, 
                {"patt":"robo3dvoando", "image":"robo3dvoando"}, 
                {"patt":"saucer", "image":"saucer"}, 
                {"patt":"temaki", "image":"temaki"}, 
                # {"patt":"antipodas", "image":"antipodas"}, # Blinking
                # {"patt":"janela", "image":"janela"}, # Gif bugging
                    # {"patt":"manekineko", "image":"manekineko"}, Not Working
                    # {"patt":"alien", "image":"alien"}, Not Working
                    # {"patt":"binoculos", "image":"janela"}, Not Working
                    # {"patt":"flyingsaucer", "image":"flyingsaucer"}, Not Working
                    # {"patt":"gueixa", "image":"gueixa"}, Not Working 
                    # {"patt":"gueixa2", "image":"gueixa2"}, Not Working
                    # {"patt":"iemanja", "image":"iemanja"}, Not Working
                    # {"patt":"pedinhazinha", "image":"pedrinhazinha"}, Not Working
                ]
            }
    return render(request, 'pwa/exhibit.jinja2', ctx)
