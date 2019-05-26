from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _

from .forms import SignupForm, UploadMarkerForm, UploadObjectForm, ArtworkForm
from .models import Marker, Object


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
    exhibits = 0
    return render(request, 'users/profile.jinja2',
    {'exhibits': exhibits})


@login_required
def artwork_creation(request):
    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES)
        form.full_clean()
        print('aaaaaaaa ', form.cleaned_data)
        if form.is_valid():
            print('aaaaaaaa ', form)
            # artwork = form.save(commit=False)
            # artwork.author = request.user.profile
            # artwork.save()
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
            'object_list': object_list
        }
    )


@login_required
def marker_upload(request):
    return upload_view(request, UploadMarkerForm, _('marker'), 'marker-upload')


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