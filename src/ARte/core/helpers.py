from django.contrib.staticfiles.templatetags.staticfiles import static
from users.views import Artwork, Exhibit, Object, Marker


def handle_upload_image(image):
    path = "core" + static(f"images/{image.name}")
    with open(path, 'wb+') as destination:
        for chunk in image.chunks():
            destination.write(chunk)


def get_stuff(model_name, model):
    def function(request):
        try:
            session_stuff = request.session[model_name]
        except(KeyError):
            request.session[model_name] = model.objects.all()
            session_stuff = request.session[model_name]
        return session_stuff
    return function

get_artworks = get_stuff('artworks', Artwork)
get_exhibits = get_stuff('exhibits', Exhibit)
get_markers = get_stuff('markers', Marker)
get_objects = get_stuff('objects', Object)