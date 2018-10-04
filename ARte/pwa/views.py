from django.shortcuts import render


def service_worker(request):
    return render(request, 'pwa/sw.js',
                  content_type='application/x-javascript')


def index(request):
    ctx = {
        "markers": [
            {"patt": "peixe", "image": "alien"},
            {"preset": "hiro", "image": "alien"},
        ]
    }
    return render(request, 'pwa/exhibit.jinja2', ctx)
