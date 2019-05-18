from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import SignupForm, UploadMarkerForm


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
    if request.method == 'POST':
        form = UploadMarkerForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UploadMarkerForm()

    return render(request, 'users/upload-marker.jinja2', {'form': form})