import json
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.http import Http404
from django.http import HttpResponse
from django.views.decorators.cache import cache_page

from .forms import SignupForm, RecoverPasswordForm, UploadMarkerForm, UploadObjectForm, ArtworkForm, ExhibitForm, ProfileForm, PasswordChangeForm
from .models import Marker, Object, Artwork, Profile
from core.models import Exhibit
from core.helpers import *

def signup(request):

    if request.method == 'POST':
        form = SignupForm(request.POST)
        
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')

    else:
        form = SignupForm()

    return render(request, 'users/signup.jinja2', {'form': form})


def recover_password(request):
    if request.method == 'POST':
        # TODO: send recovery email stuff
        return redirect('home')

    else:
        form = RecoverPasswordForm()

    return render(request, 'users/recover-password.jinja2', {'form': form})


@login_required
@cache_page(60 * 60)
def profile(request):
    profile = Profile.objects.select_related().get(user=request.user)

    exhibits = profile.exhibits.all()
    markers = profile.marker_set.all()
    objects = profile.object_set.all()
    artworks = profile.artwork_set.all()
    
    ctx = {
        'exhibits': exhibits,
        'artworks': artworks,
        'markers':markers,
        'objects':objects,
        'profile':True
    }
    return render(request, 'users/profile.jinja2', ctx)

@cache_page(60 * 60)
def get_marker(request, form):
    marker_src = form.cleaned_data['marker']
    marker_author = form.cleaned_data['marker_author']
    existent_marker = form.cleaned_data['existent_marker']
    marker = None
    
    if(marker_src and marker_author):
        marker_instance = Marker(source=marker_src, author=marker_author)
        marker = UploadMarkerForm(instance=marker_instance).save(commit=False)
        marker.owner = request.user.profile
        marker.save()
    elif(existent_marker):
        qs = Marker.objects.filter(id=existent_marker)
        if qs:
            marker = qs[0]
            marker.owner = request.user.profile

    return marker

@cache_page(60 * 60)
def get_augmented(request, form):
    object_src = form.cleaned_data['augmented']
    object_author = form.cleaned_data['augmented_author']
    existent_object = form.cleaned_data['existent_object']
    augmented = None

    if(object_src and object_author):
        object_instance = Object(source=object_src, author=object_author)
        augmented = UploadObjectForm(instance=object_instance).save(commit=False)
        augmented.owner = request.user.profile
        augmented.save()
    elif(existent_object):
        qs = Object.objects.filter(id=existent_object)
        if qs:
            augmented = qs[0]
            augmented.owner = request.user.profile

    return augmented

@login_required
@cache_page(60 * 60)
def create_artwork(request):
    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES)

        if form.is_valid():

            marker = get_marker(request,form)
            augmented = get_augmented(request, form)            
        
            if marker and augmented:
                artwork_title = form.cleaned_data['title']
                artwork_desc = form.cleaned_data['description']
                Artwork(
                    author=request.user.profile,
                    marker=marker,
                    augmented=augmented,
                    title=artwork_title,
                    description=artwork_desc
                ).save()
            return redirect('home')
    else:
        form = ArtworkForm()

    marker_list = get_markers(request)
    object_list = get_objects(request)

    return render(
        request,
        'users/artwork-create.jinja2',
        {
            'form': form, 
            'marker_list': marker_list,
            'object_list': object_list,
        }
    )



@login_required
@cache_page(60 * 60)
def create_exhibit(request):
    if request.method == 'POST':
        form = ExhibitForm(request.POST)
        if form.is_valid():
            ids = form.cleaned_data['artworks'].split(',')
            artworks = Artwork.objects.filter(id__in=ids)
            exhibit = Exhibit(
                            owner=request.user.profile,
                            name=form.cleaned_data['name'],
                            slug=form.cleaned_data['slug'],
                            )
            
            exhibit.save()
            exhibit.artworks.set(artworks)

            return redirect('home')
    else:
        form = ExhibitForm()

    artworks = Artwork.objects.filter(author=request.user.profile)

    return render(
        request,
        'users/exhibit-create.jinja2',
        {
            'form': form, 
            'artworks': artworks,
        }
    )


@login_required
def marker_upload(request):
    return upload_view(request, UploadMarkerForm, 'marker', 'marker-upload')

@cache_page(60 * 60)
def element_get(request):
    if request.GET.get('marker_id', None):
        element_type = 'marker'
        element = get_object_or_404(Marker, pk=request.GET['marker_id'])
    elif request.GET.get('object_id', None):
        element_type = 'object'
        element = get_object_or_404(Object, pk=request.GET['object_id'])
    elif request.GET.get('artwork_id', None):
        element_type = 'artwork'
        element = get_object_or_404(Artwork, pk=request.GET['artwork_id'])
        
    if element_type == 'artwork':
        data = {
	    'id_marker' : element.marker.id,
	    'id_object' : element.augmented.id,
            'type': element_type,
            'author': element.author.user.username,
            'exhibits': element.exhibits_count,
            'created_at': element.created_at.strftime('%d %b, %Y'),
            'marker': element.marker.source.url,
            'augmented': element.augmented.source.url,
            'title': element.title,
            'description': element.description,
        }
    else:
        data = {
            'id' : element.id,
            'type': element_type,
            'author': element.author,
            'owner': element.owner.user.username,
            'artworks': element.artworks_count,
            'exhibits': element.exhibits_count,
            'source': element.source.url,
            'size': element.source.size,
            'uploaded_at': element.uploaded_at.strftime('%d %b, %Y'),
        }

    serialized = json.dumps(data)

    return HttpResponse(serialized, content_type='application/json')


@login_required
def object_upload(request):
    return upload_view(request, UploadObjectForm, 'object', 'object-upload')


def upload_view(request, form_class, form_type, route):
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.owner = request.user.profile
            upload.save()
            return redirect('home')
    else:
        form = form_class()

    return render(request,'users/upload.jinja2',
        {'form_type': form_type, 'form': form, 'route': route})


@login_required
@cache_page(60 * 60)
def edit_artwork(request): 
    id = request.GET.get("id","-1")
    model = Artwork.objects.filter(id=id)
    if(not model or model.first().author != Profile.objects.get(user=request.user)):
        raise Http404

    if(request.method == "POST"):
        form = ArtworkForm(request.POST, request.FILES)

        form.full_clean()
        if form.is_valid():
            model_data={
                "marker":get_marker(request,form),
                "augmented": get_augmented(request, form),
                "title": form.cleaned_data["title"],
                "description": form.cleaned_data["description"],
            }
            print(model_data['augmented'])
            model.update(**model_data)
            return redirect('profile')

    model = model.first()
    model_data = {
        "marker": model.marker,
        "marker_author": model.marker.author,
        "augmented": model.augmented,
        "augmented_author": model.augmented.author,
        "title": model.title,
        "description": model.description,
        "existent_marker": model.marker.id,
        "existent_object": model.augmented.id,
    }

    return render(
        request,
        'users/artwork-create.jinja2',
        {
            'form': ArtworkForm(initial=model_data), 
            'marker_list': get_markers(request),
            'object_list': get_objects(request),
            'selected_marker': model.marker.id,
            'selected_object': model.augmented.id
        }
    )


@login_required
@cache_page(60 * 60)
def edit_exhibit(request): 
    id = request.GET.get("id","-1")
    model = Exhibit.objects.filter(id=id)
    if(not model or model.first().owner != Profile.objects.get(user=request.user)):
        raise Http404

    if(request.method == "POST"):
        form = ExhibitForm(request.POST)

        form.full_clean()
        if form.is_valid():
            ids = form.cleaned_data['artworks'].split(',')
            artworks = Artwork.objects.filter(id__in=ids)

            model_data={
                "name":form.cleaned_data["name"],
                "slug": form.cleaned_data["slug"],
            }
            model.update(**model_data)
            model = model.first()
            model.artworks.set(artworks)
            
            return redirect('profile')

    model = model.first()
    model_artworks = ""
    for artwork in model.artworks.all():
        model_artworks += str(artwork.id) + ","

    model_artworks = model_artworks[:-1]

    model_data = {
        "name": model.name,
        "slug": model.slug,
        "artworks": model_artworks
    }

    artworks = Artwork.objects.filter(author=request.user.profile)
    return render(
        request,
        'users/exhibit-create.jinja2',
        {
            'form': ExhibitForm(initial=model_data), 
            'artworks': artworks,
            'selected_artworks': model_artworks,
        }
    )

@login_required
def edit_password(request):

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('profile')
        else:
            profile = Profile.objects.get(user=request.user)
            ctx={
                'form_password': PasswordChangeForm(request.user), 
                'form_profile': ProfileForm(instance=profile)
            }
            return render(request,'users/profile-edit.jinja2',ctx)
    return Http404

@login_required
def edit_profile(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)

        if form.is_valid():
            profile = form.save(commit=False)
            user = profile.user
            user.email = form.cleaned_data['email']
            user.username = form.cleaned_data['username']
            user.save(force_update=True)
            profile.save()

            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    return render(
        request,
        'users/profile-edit.jinja2',
        {
            'form_profile': form,
            'form_password': PasswordChangeForm(request.user),
        }
    )

@login_required
def delete(request):
    content_type = request.GET.get('content_type', None)

    if content_type == 'marker':
       delete_content(Marker, request.user, request.GET.get('id', -1))
    elif content_type == 'object':
       delete_content(Object, request.user, request.GET.get('id', -1))
    elif content_type == 'artwork':
       delete_content(Artwork, request.user, request.GET.get('id', -1))
    elif content_type == 'exhibit':
       delete_content(Exhibit, request.user, request.GET.get('id', -1))


    return redirect('profile')

def delete_content(model, user, instance_id):
    qs = model.objects.filter(id=instance_id)
    if qs:
        instance = qs[0]
        if isinstance(instance, Artwork):
            if instance.author == user.profile and not instance.in_use:
                instance.delete()
        elif instance.owner == user.profile:
            if isinstance(instance, Exhibit) or not instance.in_use:
                instance.delete()
