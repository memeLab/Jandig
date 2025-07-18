import logging

from django.conf import settings
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods

from .forms import (
    PasswordChangeForm,
    ProfileForm,
    SignupForm,
)
from .models import Profile
from .services import BOT_SCORE, create_assessment

log = logging.getLogger(__file__)

User = get_user_model()


def signup(request):
    if request.method == "POST":
        if settings.RECAPTCHA_ENABLED:
            recaptcha_token = request.POST.get("g-recaptcha-response")
            if not recaptcha_token:
                return JsonResponse({"error": "Invalid Request"}, status=400)
            assessment = create_assessment(
                token=recaptcha_token, recaptcha_action="sign_up"
            )
            score = assessment.get("riskAnalysis", {}).get("score", -1)
            if score <= BOT_SCORE:
                return JsonResponse({"error": "Invalid Request"}, status=400)

        form = SignupForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect("home")

    else:
        form = SignupForm()

    return render(
        request,
        "users/signup.jinja2",
        {
            "form": form,
            "recaptcha_enabled": settings.RECAPTCHA_ENABLED,
            "recaptcha_site_key": settings.RECAPTCHA_SITE_KEY,
        },
    )


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = "users/reset-password/password_reset.jinja2"
    email_template_name = "users/reset-password/password_reset_email.html"
    subject_template_name = "users/reset-password/password_reset_subject.txt"
    success_message = _(
        "We've emailed you instructions for setting your password, "
        "if an account exists with the email you entered. You should receive them shortly."
        " If you don't receive an email, "
        "please make sure you've entered the address you registered with, and check your spam folder."
    )
    success_url = reverse_lazy("home")


@login_required
@require_http_methods(["GET"])
def profile(request):
    user = request.GET.get("user")

    if not user:
        user = request.user

    profile = Profile.objects.prefetch_related(
        "exhibits__artworks",
        "artworks__exhibits",
        "artworks__marker",
        "artworks__augmented",
        "markers__artworks",
        "ar_objects__artworks",
    ).get(user=user)

    exhibits = profile.exhibits.all()
    artworks = profile.artworks.all()
    markers = profile.markers.all()
    objects = profile.ar_objects.all()

    ctx = {
        "exhibits": exhibits,
        "artworks": artworks,
        "markers": markers,
        "objects": objects,
        "profile": True,
        "button_enable": True if user else False,
    }
    return render(request, "users/profile.jinja2", ctx)


@login_required
def edit_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect("profile")

        profile = Profile.objects.get(user=request.user)
        ctx = {
            "form_password": PasswordChangeForm(request.user),
            "form_profile": ProfileForm(instance=profile),
        }
        return render(request, "users/profile-edit.jinja2", ctx)
    return Http404


@login_required
def edit_profile(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)

        if form.is_valid():
            profile = form.save(commit=False)
            user = profile.user
            user.email = form.cleaned_data["email"]
            user.username = form.cleaned_data["username"]
            user.save(force_update=True)
            profile.save()

            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)

    return render(
        request,
        "users/profile-edit.jinja2",
        {
            "form_profile": form,
            "form_password": PasswordChangeForm(request.user),
        },
    )
