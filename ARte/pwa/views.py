from django.shortcuts import render


def service_worker(request):
    return render(request, 'pwa/sw.js',
                  content_type='application/x-javascript')

def index(request):
    return render(request, 'pwa/index.html')
