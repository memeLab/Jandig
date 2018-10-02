from django.shortcuts import render


def index(request):
    ctx = {"markers":[
                {"patt":"peixe", "image":"alien"},
                {"preset":"hiro", "image":"alien"},
                ]
            }
    return render(request, 'pwa/exhibit.jinja2', ctx)
