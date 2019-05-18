from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _


from .forms import SignupForm, UploadMarkerForm, UploadObjectForm


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
    return render(request, 'users/profile.jinja2')


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
            form.save()
            return redirect('home')
    else:
        form = form_class()

    return render(request,'users/upload.jinja2',
        {'form_type': form_type, 'form': form, 'route': route})