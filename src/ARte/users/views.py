import json
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse

from .forms import SignupForm, UploadMarkerForm, UploadObjectForm, ArtworkForm, ExhibitForm
from .models import Marker, Object, Artwork, Profile
from core.models import Exhibit


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


@login_required
def profile(request): 
    profile = Profile.objects.get(user=request.user)
    
    exhibits = Exhibit.objects.filter(owner=profile)
    artworks = Artwork.objects.filter(author=profile)
    markers = Marker.objects.filter(owner=profile)
    objects = Object.objects.filter(owner=profile)
    ctx = {
        'exhibits': exhibits,
        'artworks': artworks,
        'markers':markers,
        'objects':objects,
        'profile':True
    }
    return render(request, 'users/profile.jinja2', ctx)


@login_required
def artwork_creation(request):
    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES)

        if form.is_valid():
            marker_src = form.cleaned_data['marker']
            marker_author = form.cleaned_data['marker_author']
            object_src = form.cleaned_data['augmented']
            object_author = form.cleaned_data['augmented_author']

            existent_marker = form.cleaned_data['existent_marker']
            existent_object = form.cleaned_data['existent_object']

            marker = None
            augmented = None

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

    marker_list = Marker.objects.all()
    object_list = Object.objects.all()

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
def exhibit_creation(request):
    if request.method == 'POST':
        form = ExhibitForm(request.POST)
        form.full_clean()
        print(form.cleaned_data['artworks'])

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
    return upload_view(request, UploadMarkerForm, _('marker'), 'marker-upload')


def marker_get(request):
    marker = get_object_or_404(Marker, pk=request.GET['marker_id'])
    data = {
        'marker_author': marker.author,
        'marker_owner': marker.owner.user.username,
        'marker_artworks': marker.artworks_count,
        'marker_exhibits': marker.exhibits_count,
        'marker_source': marker.source.url,
        'marker_size': marker.source.size,
        'marker_uploaded_at': marker.uploaded_at.strftime('%d %b, %Y'),
    }
    serialized = json.dumps(data)

    return HttpResponse(serialized, content_type='application/json')


@login_required
def object_upload(request):
    return upload_view(request, UploadObjectForm, _('object'), 'object-upload')


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