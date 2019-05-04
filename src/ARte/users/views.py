from django.shortcuts import render

from .forms import SignupForm


def signup(request):
    
    if request.method == 'GET':
        return render(request, 'users/signup.jinja2', {'form': SignupForm()})