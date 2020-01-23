from django.contrib.staticfiles.templatetags.staticfiles import static
from users.models import Artwork, Object, Marker, Profile
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

def get_update_function_for_all(model_name,model):
    def update_from_db(request):
        request.session[model_name] = model.objects.all()
        session_items = request.session[model_name]
        return session_items
    return update_from_db

update_artworks = get_update_function_for_all('artworks',Artwork)
update_exhibits = get_update_function_for_all('exhibits',Exhibit)
update_markers = get_update_function_for_all('markers',Marker)
update_objects = get_update_function_for_all('objects',Object)

def get_profile(request):
    try:
        session_profile = request.session['profile']
    except(KeyError):
        request.session['profile'] = Profile.objects.get(user=request.user)
        session_profile = request.session['profile']
    return session_profile

def get_function_for_user(model_name, model):
    def get_all_from_db(request):
        try:
            session_items = request.session[model_name]
        except(KeyError):
            request.session[model_name] = model.objects.filter(owner=get_profile(request))
            session_items = request.session[model_name]
        return session_items
    return get_all_from_db
        
get_user_exhibits = get_function_for_user('exhibits', Exhibit)
get_user_markers = get_function_for_user('markers', Marker)
get_user_objects = get_function_for_user('objects', Object)

# Artworks need to be different, because they have author and not a owner.
# I'm not renaming the field to avoid generating a new db migration
def get_user_artworks(request):
    try:
        session_items = request.session['artworks']
    except(KeyError):
        request.session['artworks'] = Artwork.objects.filter(author=get_profile(request))
        session_items = request.session['artworks']
    return session_items
    