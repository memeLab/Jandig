from django.contrib.staticfiles.templatetags.staticfiles import static
from users.models import Artwork, Object, Marker
from core.models import Exhibit

def handle_upload_image(image):
    path = "core" + static(f"images/{image.name}")
    with open(path, 'wb+') as destination:
        for chunk in image.chunks():
            destination.write(chunk)


def get_function_for_all(model_name, model):
    def get_all_from_db(request):
        try:
            session_items = request.session[model_name]
        except(KeyError):
            request.session[model_name] = model.objects.all()
            session_items = request.session[model_name]
        return session_items
    return get_all_from_db

get_artworks = get_function_for_all('artworks', Artwork)
get_exhibits = get_function_for_all('exhibits', Exhibit)
get_markers = get_function_for_all('markers', Marker)
get_objects = get_function_for_all('objects', Object)

get_artworks = get_stuff('artworks', Artwork)
get_exhibits = get_stuff('exhibits', Exhibit)
get_markers = get_stuff('markers', Marker)