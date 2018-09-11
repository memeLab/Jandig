from django.shortcuts import render


def index(request):
    ctx = {"markers":[
                {"patt":"peixe", "image":"peixe"},
                ]
            }
    return render(request, 'pwa/exhibit.jinja2', ctx)
