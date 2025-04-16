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
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods

from core.models import Artwork, Exhibit, Marker, Object

from .forms import (
    ArtworkForm,
    ExhibitForm,
    PasswordChangeForm,
    ProfileForm,
    SignupForm,
    UploadMarkerForm,
    UploadObjectForm,
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


@cache_page(60 * 60)
def get_element(request, form, form_class, form_type, source, author, existent_element):
    element = None

    if source and author:
        instance = form_type(source=source, author=author)
        element = form_class(instance=instance).save(commit=False)
        element.save()
    elif existent_element:
        qs = form_type.objects.filter(id=existent_element)
        if qs:
            element = qs[0]
            element.owner = request.user.profile

    return element


@cache_page(60 * 60)
def get_marker(request, form):
    marker_src = form.cleaned_data["marker"]
    marker_author = form.cleaned_data["marker_author"]
    existent_marker = form.cleaned_data["existent_marker"]

    return get_element(
        request,
        form,
        UploadMarkerForm,
        Marker,
        source=marker_src,
        author=marker_author,
        existent_element=existent_marker,
    )


@cache_page(60 * 60)
def get_augmented(request, form):
    object_src = form.cleaned_data["augmented"]
    object_author = form.cleaned_data["augmented_author"]
    existent_object = form.cleaned_data["existent_object"]

    return get_element(
        request,
        form,
        UploadObjectForm,
        Object,
        source=object_src,
        author=object_author,
        existent_element=existent_object,
    )


@login_required
def create_artwork(request):
    if request.method == "POST":
        form = ArtworkForm(request.POST, request.FILES)

        if form.is_valid():
            marker = get_marker(request, form)
            augmented = get_augmented(request, form)

            if marker and augmented:
                artwork_title = form.cleaned_data["title"]
                artwork_desc = form.cleaned_data["description"]
                Artwork(
                    author=request.user.profile,
                    marker=marker,
                    augmented=augmented,
                    title=artwork_title,
                    description=artwork_desc,
                ).save()
            return redirect("profile")
    else:
        form = ArtworkForm()

    marker_list = Marker.objects.all()
    object_list = Object.objects.all()

    return render(
        request,
        "users/artwork.jinja2",
        {
            "form": form,
            "marker_list": marker_list,
            "object_list": object_list,
        },
    )


@login_required
def create_exhibit(request):
    if request.method == "POST":
        form = ExhibitForm(request.POST)
        if form.is_valid():
            ids = form.cleaned_data["artworks"].split(",")
            artworks = Artwork.objects.filter(id__in=ids).order_by("-id")
            exhibit = Exhibit(
                owner=request.user.profile,
                name=form.cleaned_data["name"],
                slug=form.cleaned_data["slug"],
            )

            exhibit.save()
            exhibit.artworks.set(artworks)

            return redirect("profile")
    else:
        form = ExhibitForm()

    artworks = Artwork.objects.all().order_by("-id")

    return render(
        request,
        "users/exhibit-create.jinja2",
        {
            "form": form,
            "artworks": artworks,
        },
    )


def upload_elements(request, form_class, form_type, route):
    if request.method == "POST":
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.owner = request.user.profile
            upload.save()
            return redirect("profile")
    else:
        form = form_class()

    if form_type == "marker":
        return render(
            request,
            "users/upload-marker.jinja2",
            {"form_type": form_type, "form": form, "route": route, "edit": False},
        )

    return render(
        request,
        "users/upload-object.jinja2",
        {"form_type": form_type, "form": form, "route": route, "edit": False},
    )


@login_required
def object_upload(request):
    return upload_elements(request, UploadObjectForm, "object", "object-upload")


@login_required
def marker_upload(request):
    return upload_elements(request, UploadMarkerForm, "marker", "marker-upload")


def edit_elements(request, form_class, route, model, model_data):
    if not model or model.owner != Profile.objects.get(user=request.user):
        raise Http404

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=model)

        form.full_clean()
        if form.is_valid():
            form.save()
            return redirect("profile")

        log.warning(form.errors)

    return render(
        request,
        route,
        {
            "form": form_class(initial=model_data),
            "model": model,
        },
    )


@login_required
def edit_object(request):
    index = request.GET.get("id", "-1")
    model = Object.objects.get(id=index)

    model_data = {
        "source": model.source,
        "uploaded_at": model.uploaded_at,
        "author": model.author,
        "scale": model.scale,
        "position": model.position,
        "rotation": model.rotation,
        "title": model.title,
    }
    return edit_elements(
        request,
        UploadObjectForm,
        route="users/edit-object.jinja2",
        model=model,
        model_data=model_data,
    )


@login_required
def edit_marker(request):
    index = request.GET.get("id", "-1")
    model = Marker.objects.get(id=index)

    model_data = {
        "source": model.source,
        "uploaded_at": model.uploaded_at,
        "author": model.author,
        "patt": model.patt,
        "title": model.title,
    }

    return edit_elements(
        request,
        UploadMarkerForm,
        route="users/edit-marker.jinja2",
        model=model,
        model_data=model_data,
    )


@login_required
def edit_artwork(request):
    index = request.GET.get("id", "-1")
    model = Artwork.objects.filter(id=index).order_by("-id")
    if not model or model.first().author != Profile.objects.get(user=request.user):
        raise Http404

    if request.method == "POST":
        form = ArtworkForm(request.POST, request.FILES)

        form.full_clean()
        if form.is_valid():
            model_data = {
                "marker": get_marker(request, form),
                "augmented": get_augmented(request, form),
                "title": form.cleaned_data["title"],
                "description": form.cleaned_data["description"],
            }
            print(model_data["augmented"])
            model.update(**model_data)
            return redirect("profile")

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
        "users/artwork.jinja2",
        {
            "form": ArtworkForm(initial=model_data),
            "marker_list": Marker.objects.all(),
            "object_list": Object.objects.all(),
            "selected_marker": model.marker.id,
            "selected_object": model.augmented.id,
        },
    )


@login_required
def edit_exhibit(request):
    index = request.GET.get("id", "-1")
    model = Exhibit.objects.filter(id=index)
    if not model or model.first().owner != Profile.objects.get(user=request.user):
        raise Http404

    if request.method == "POST":
        form = ExhibitForm(request.POST)

        form.full_clean()
        if form.is_valid():
            ids = form.cleaned_data["artworks"].split(",")
            artworks = Artwork.objects.filter(id__in=ids).order_by("-id")

            model_data = {
                "name": form.cleaned_data["name"],
                "slug": form.cleaned_data["slug"],
            }
            model.update(**model_data)
            model = model.first()
            model.artworks.set(artworks)

            return redirect("profile")

    model = model.first()
    model_artworks = ""
    for artwork in model.artworks.all():
        model_artworks += str(artwork.id) + ","

    model_artworks = model_artworks[:-1]

    model_data = {"name": model.name, "slug": model.slug, "artworks": model_artworks}

    artworks = Artwork.objects.filter(author=request.user.profile).order_by("-id")

    return render(
        request,
        "users/exhibit-edit.jinja2",
        {
            "form": ExhibitForm(initial=model_data),
            "artworks": artworks,
            "selected_artworks": model_artworks,
        },
    )


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


@login_required
@require_http_methods(["GET"])
def delete(request):
    content_type = request.GET.get("content_type", None)

    if content_type == "marker":
        delete_content(Marker, request.user, request.GET.get("id", -1))
    elif content_type == "object":
        delete_content(Object, request.user, request.GET.get("id", -1))
    elif content_type == "artwork":
        delete_content(Artwork, request.user, request.GET.get("id", -1))
    elif content_type == "exhibit":
        delete_content(Exhibit, request.user, request.GET.get("id", -1))
    return redirect("profile")


def delete_content(model, user, instance_id):
    qs = model.objects.filter(id=instance_id)

    if qs:
        instance = qs[0]
        if user.has_perm("users.moderator"):
            delete_content_Moderator(instance, user, model)
        else:
            isArtwork = isinstance(instance, Artwork)
            if isArtwork:
                hasPermission = instance.author == user.profile
            else:
                hasPermission = instance.owner == user.profile

            isInstanceSameTypeofModel = isinstance(instance, model)
            if isInstanceSameTypeofModel and hasPermission:
                instance.delete()


def delete_content_Moderator(instance, user, model):
    isInstanceSameTypeofModel = isinstance(instance, model)
    isObject = isinstance(instance, Object)
    isMarker = isinstance(instance, Marker)
    isArtwork = isinstance(instance, Artwork)

    if isInstanceSameTypeofModel or not instance.in_use:
        instance.delete()
    elif instance.in_use:
        if isObject:
            artworkIn = Artwork.objects.filter(augmented=instance)
            artworkIn.delete()
            instance.delete()
        elif isMarker:
            artworkIn = Artwork.objects.filter(marker=instance)
            artworkIn.delete()
            instance.delete()
        elif isArtwork:
            instance.delete()


@login_required
@require_http_methods(["GET"])
def mod_delete(request):
    content_type = request.GET.get("content_type", None)
    if content_type == "marker":
        delete_content(Marker, request.user, request.GET.get("instance_id", -1))
    elif content_type == "object":
        delete_content(Object, request.user, request.GET.get("instance_id", -1))
    elif content_type == "artwork":
        delete_content(Artwork, request.user, request.GET.get("instance_id", -1))
    elif content_type == "exhibit":
        delete_content(Exhibit, request.user, request.GET.get("id", -1))
    return redirect("moderator-page")


def mod(request):
    ctx = {
        "objects": Object.objects.all(),
        "markers": Marker.objects.all(),
        "artworks": Artwork.objects.all().order_by("-id"),
        "exhibits": Exhibit.objects.all(),
        "permission": request.user.has_perm("users.moderator"),
    }
    return render(request, "users/moderator-page.jinja2", ctx)


def permission_denied(request):
    return render(request, "users/permission-denied.jinja2")
