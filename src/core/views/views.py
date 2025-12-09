from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from core.forms import (
    ArtworkForm,
    ExhibitForm,
    ExhibitSelectForm,
    SoundForm,
    UploadMarkerForm,
    UploadObjectForm,
)
from core.models import (
    Artwork,
    Exhibit,
    ExhibitTypes,
    Marker,
    Object,
    ObjectExtensions,
    Sound,
)
from users.models import Profile

COLLECTION_PAGE = "core/collection.jinja2"


@require_http_methods(["GET"])
def collection(request):
    ar_exhibits = (
        Exhibit.objects.select_related("owner", "owner__user")
        .prefetch_related("artworks")
        .filter(exhibit_type=ExhibitTypes.AR)
        .all()
        .order_by("-created")[:4]
    )
    mr_exhibits = (
        Exhibit.objects.select_related("owner", "owner__user")
        .prefetch_related("artworks")
        .filter(exhibit_type=ExhibitTypes.MR)
        .all()
        .order_by("-created")[:4]
    )
    artworks = (
        Artwork.objects.select_related("author", "author__user", "marker", "augmented")
        .all()
        .order_by("-created")[:6]
    )
    markers = Marker.objects.all().order_by("-created")[:8]
    objects = Object.objects.all().order_by("-created")[:8]
    sounds = Sound.objects.all().order_by("-created")[:8]

    ctx = {
        "artworks": artworks,
        "ar_exhibits": ar_exhibits,
        "mr_exhibits": mr_exhibits,
        "markers": markers,
        "objects": objects,
        "sounds": sounds,
        "seeall": False,
    }

    return render(request, COLLECTION_PAGE, ctx)


@require_http_methods(["GET"])
def see_all(request, which=""):
    request_type = request.GET.get("which", which)
    if request_type not in [
        "object",
        "marker",
        "artwork",
        "ar-exhibit",
        "mr-exhibit",
        "sound",
    ]:
        # Invalid request type, return to collection
        return redirect("collection")
    ctx = {}

    per_page = settings.PAGE_SIZE
    page_parameter = request.GET.get("page", 1)

    try:
        # Bots insert random strings in the page parameter
        page = int(page_parameter)
    except ValueError:
        page = 1

    data_types = {
        "object": Object.objects.all().order_by("-created"),
        "marker": Marker.objects.all().order_by("-created"),
        "artwork": Artwork.objects.prefetch_related("marker", "augmented")
        .all()
        .order_by("-created"),
        "ar-exhibit": Exhibit.objects.select_related("owner", "owner__user")
        .prefetch_related("artworks")
        .filter(exhibit_type=ExhibitTypes.AR)
        .all()
        .order_by("-created"),
        "mr-exhibit": Exhibit.objects.select_related("owner", "owner__user")
        .prefetch_related("artworks")
        .filter(exhibit_type=ExhibitTypes.MR)
        .all()
        .order_by("-created"),
        "sound": Sound.objects.all().order_by("-created"),
    }

    data = data_types.get(request_type)
    if data:
        paginator = Paginator(data, per_page)
        if page > paginator.num_pages:
            return redirect("see_all", request_type)
        paginated_data = paginator.get_page(page)
        paginated_data.adjusted_elided_pages = paginator.get_elided_page_range(page)
        # We need to match the variable name in the collection template context
        collection_page_variable_name = f"{request_type.replace('-', '_')}s"
        ctx = {
            collection_page_variable_name: paginated_data,
            "seeall": True,
        }
    return render(request, COLLECTION_PAGE, ctx)


def delete_content(model, user, instance_id):
    qs = model.objects.filter(id=instance_id)

    if qs:
        instance = qs[0]

        is_artwork = isinstance(instance, Artwork)
        if is_artwork:
            has_permission = instance.author == user.profile
        else:
            has_permission = instance.owner == user.profile

        is_instance_same_type_of_model = isinstance(instance, model)
        if is_instance_same_type_of_model and has_permission:
            instance.delete()


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
    elif content_type == "ar-exhibit" or content_type == "mr-exhibit":
        delete_content(Exhibit, request.user, request.GET.get("id", -1))
    elif content_type == "sound":
        delete_content(Sound, request.user, request.GET.get("id", -1))
    return redirect("profile")


@login_required
def object_upload(request):
    """Upload an object file and generate a thumbnail if it's a GLB file."""
    if request.method == "POST":
        form = UploadObjectForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user.profile
            obj.save()
            return redirect("profile")
    else:
        form = UploadObjectForm()

    sounds = Sound.objects.all().order_by("-created")
    paginator_sounds = Paginator(sounds, settings.MODAL_PAGE_SIZE)
    return render(
        request,
        "core/upload-object.jinja2",
        {
            "form": form,
            "edit": False,
            "sounds": sounds[: settings.MODAL_PAGE_SIZE],
            "total_sound_pages": paginator_sounds.num_pages,
        },
    )


@login_required
def marker_upload(request):
    if request.method == "POST":
        form = UploadMarkerForm(request.POST, request.FILES)
        if form.is_valid():
            marker = form.save(commit=False)
            marker.owner = request.user.profile
            marker.save()
            return redirect("profile")
    else:
        form = UploadMarkerForm()

    return render(
        request,
        "core/upload-marker.jinja2",
        {"form_type": "marker", "form": form, "route": "marker-upload", "edit": False},
    )


@login_required
def edit_marker(request):
    index = request.GET.get("id", "-1")
    model = Marker.objects.get(id=index)

    model_data = {
        "source": model.source,
        "created": model.created,
        "author": model.author,
        "patt": model.patt,
        "title": model.title,
    }

    if not model or model.owner != Profile.objects.get(user=request.user):
        raise Http404

    if request.method == "POST":
        form = UploadMarkerForm(request.POST, request.FILES, instance=model)

        form.full_clean()
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = UploadMarkerForm(initial=model_data)

    return render(
        request,
        "core/upload-marker.jinja2",
        {
            "form": form,
            "model": model,
            "edit": True,
        },
    )


@login_required
def edit_object(request):
    index = request.GET.get("id", "-1")
    model = Object.objects.get(id=index)

    model_data = {
        "source": model.source,
        "created": model.created,
        "author": model.author,
        "title": model.title,
        "thumbnail": model.thumbnail,
    }
    if not model or model.owner != Profile.objects.get(user=request.user):
        raise Http404

    if request.method == "POST":
        form = UploadObjectForm(request.POST, request.FILES, instance=model)

        form.full_clean()
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = UploadObjectForm(initial=model_data)

    sounds = Sound.objects.all().order_by("-created")
    paginator_sounds = Paginator(sounds, settings.MODAL_PAGE_SIZE)

    return render(
        request,
        "core/upload-object.jinja2",
        {
            "form": form,
            "model": model,
            "edit": True,
            "sounds": sounds[: settings.MODAL_PAGE_SIZE],
            "selected_sound": model.sound.id if model.sound else None,
            "total_sound_pages": paginator_sounds.num_pages,
        },
    )


def _handle_artwork_form(request, user_profile, artwork_instance=None):
    """Helper function to handle artwork form processing for both create and edit operations."""

    if request.method == "POST":
        form = ArtworkForm(request.POST, request.FILES, instance=artwork_instance)

        if form.is_valid():
            artwork = form.save(commit=False)
            artwork.author = user_profile
            artwork.save()
            return redirect("profile")
    else:
        form = ArtworkForm(instance=artwork_instance)
    context = _get_artwork_context_data(form, artwork_instance)
    return render(request, "core/upload-artwork.jinja2", context)


def _get_artwork_context_data(form, artwork_instance=None):
    """Helper function to prepare context data for artwork templates."""
    marker_list = Marker.objects.all().order_by("-created")
    object_list = (
        Object.objects.exclude(file_extension=ObjectExtensions.GLB)
        .all()
        .order_by("-created")
    )
    sound_list = Sound.objects.all().order_by("-created")
    paginator_marker = Paginator(marker_list, settings.MODAL_PAGE_SIZE)
    paginator_object = Paginator(object_list, settings.MODAL_PAGE_SIZE)
    paginator_sound = Paginator(sound_list, settings.MODAL_PAGE_SIZE)

    context = {
        "form": form,
        "sound_list": sound_list[: settings.MODAL_PAGE_SIZE],
        "marker_list": marker_list[: settings.MODAL_PAGE_SIZE],
        "object_list": object_list[: settings.MODAL_PAGE_SIZE],
        "total_marker_pages": paginator_marker.num_pages,
        "total_object_pages": paginator_object.num_pages,
        "total_sound_pages": paginator_sound.num_pages,
    }

    if artwork_instance:
        context.update(
            {
                "selected_marker": artwork_instance.marker.id,
                "selected_object": artwork_instance.augmented.id,
            }
        )
        if artwork_instance.sound:
            context.update(
                {
                    "selected_sound": artwork_instance.sound.id,
                }
            )

    return context


@login_required
def create_artwork(request):
    return _handle_artwork_form(request, request.user.profile)


@login_required
def edit_artwork(request):
    index = request.GET.get("id", "-1")
    try:
        model = Artwork.objects.get(id=index)
    except Artwork.DoesNotExist:
        raise Http404

    if model.author != Profile.objects.get(user=request.user):
        raise Http404

    return _handle_artwork_form(request, request.user.profile, model)


@require_http_methods(["GET"])
def artwork_preview(request):
    artwork_id = request.GET.get("id")

    ctx = {
        "artworks": Artwork.objects.filter(id=artwork_id).order_by("-id"),
    }
    return render(request, "core/exhibit.jinja2", ctx)


@login_required
def get_element(request):
    if request.htmx:
        page = int(request.GET.get("page", "1"))
        match element_type := request.GET.get("element_type"):
            case "object":
                qs = Object.objects.all().order_by("-created")
                if request.GET.get("exclude_glb", "false") == "true":
                    qs = qs.exclude(file_extension=ObjectExtensions.GLB)
            case "marker":
                qs = Marker.objects.all().order_by("-created")
            case "sound":
                qs = Sound.objects.all().order_by("-created")
            case _:
                raise Http404("Invalid element type")

        paginator = Paginator(qs, settings.MODAL_PAGE_SIZE)
        if page > paginator.num_pages:
            page = paginator.num_pages

        return render(
            request,
            "core/components/item-list.jinja2",
            {
                "repository_list": paginator.get_page(page),
                "element_type": element_type,
                "htmx": "false",
            },
        )
    raise Http404


def _handle_exhibit_form(
    request, user_profile, exhibit_instance=None, exhibit_type=None
):
    """Helper function to handle exhibit form processing for both create and edit operations."""
    is_edit = exhibit_instance is not None

    if request.method == "POST":
        form = ExhibitForm(request.POST, instance=exhibit_instance)
        form.full_clean()

        if form.is_valid():
            exhibit = form.save(commit=False)
            exhibit.owner = user_profile
            form.save()
            return redirect("profile")
        else:
            if exhibit_type == ExhibitTypes.MR:
                context = _get_mr_exhibit_context_data(form, edit=is_edit)
                return render(request, "core/exhibit_create_mr.jinja2", context)
            context = _get_ar_exhibit_context_data(user_profile, form, edit=is_edit)
            return render(request, "core/exhibit_create_ar.jinja2", context)
    else:
        form = ExhibitForm(instance=exhibit_instance)
        if exhibit_type == ExhibitTypes.MR:
            context = _get_mr_exhibit_context_data(form, edit=is_edit)
            return render(request, "core/exhibit_create_mr.jinja2", context)
        context = _get_ar_exhibit_context_data(user_profile, form, edit=is_edit)
        return render(request, "core/exhibit_create_ar.jinja2", context)


def _get_mr_exhibit_context_data(form, edit=False):
    """Helper method to prepare context data for exhibit templates."""
    objects = Object.objects.all().order_by("-created")
    sounds = Sound.objects.all().order_by("-created")

    paginator_objects = Paginator(objects, settings.MODAL_PAGE_SIZE)
    paginator_sounds = Paginator(sounds, settings.MODAL_PAGE_SIZE)

    context = {
        "form": form,
        "objects": objects[: settings.MODAL_PAGE_SIZE],
        "sounds": sounds[: settings.MODAL_PAGE_SIZE],
        "total_object_pages": paginator_objects.num_pages,
        "total_sound_pages": paginator_sounds.num_pages,
    }

    if edit:
        selected_objects = ",".join(
            str(augmented.id) for augmented in form.instance.augmenteds.all()
        )
        selected_sounds = ",".join(
            str(sound.id) for sound in form.instance.sounds.all()
        )
        context.update(
            {
                "selected_objects": selected_objects,
                "selected_sounds": selected_sounds,
                "edit": edit,
            }
        )

    return context


def _get_ar_exhibit_context_data(user_profile, form, edit=False):
    """Helper method to prepare context data for exhibit templates."""
    artworks = Artwork.objects.filter(author=user_profile).order_by("-id")

    context = {
        "form": form,
        "artworks": artworks,
    }

    if edit:
        selected_artworks = ",".join(
            str(artwork.id) for artwork in form.instance.artworks.all()
        )

        context.update(
            {
                "selected_artworks": selected_artworks,
                "edit": edit,
            }
        )

    return context


@login_required
def create_or_edit_ar_exhibit(request):
    return create_or_edit_exhibit(request, ExhibitTypes.AR)


@login_required
def create_or_edit_mr_exhibit(request):
    return create_or_edit_exhibit(request, ExhibitTypes.MR)


def create_or_edit_exhibit(request, exhibit_type=None):
    index = request.GET.get("id", "-1")
    model = None
    if index != "-1":
        try:
            index = int(index)
        except ValueError:
            raise Http404

        try:
            model = Exhibit.objects.get(id=index)
        except Exhibit.DoesNotExist:
            raise Http404

        if model.owner != Profile.objects.get(user=request.user):
            raise Http404

    return _handle_exhibit_form(request, request.user.profile, model, exhibit_type)


@require_http_methods(["GET"])
def exhibit_detail(request):
    index = request.GET.get("id", -1)
    # Bots insert random strings in the id parameter, index should be an integer
    try:
        index = int(index)
    except ValueError:
        raise Http404
    exhibit = get_object_or_404(Exhibit.objects.prefetch_related("artworks"), id=index)
    ctx = {
        "exhibit": exhibit,
        "exhibitImage": "https://cdn3.iconfinder.com/data/icons/basic-mobile-part-2/512/painter-512.png",
        "artworks": exhibit.artworks.select_related("marker", "augmented").all(),
        "objects": exhibit.augmenteds.all(),
        "sounds": exhibit.sounds.all(),
    }
    return render(request, "core/exhibit_detail.jinja2", ctx)


@login_required
def sound_upload(request):
    if request.method == "POST":
        form = SoundForm(request.POST, request.FILES)
        if form.is_valid():
            sound = form.save(commit=False)
            sound.owner = request.user.profile
            sound.save()
            return redirect("profile")
    else:
        form = SoundForm()
    return render(request, "core/upload-sound.jinja2", {"form": form})


@login_required
def edit_sound(request):
    index = request.GET.get("id", "-1")
    try:
        model = Sound.objects.get(id=index)
    except Sound.DoesNotExist:
        raise Http404

    if model.owner != Profile.objects.get(user=request.user):
        raise Http404

    if request.method == "POST":
        form = SoundForm(request.POST, request.FILES, instance=model)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = SoundForm(instance=model)

    return render(request, "core/upload-sound.jinja2", {"form": form, "model": model})


def exhibit_select(request):
    if request.method == "POST":
        form = ExhibitSelectForm(request.POST)
        if form.is_valid():
            exhibit = form.cleaned_data.get("exhibit")
            return redirect("/" + exhibit.slug)
    else:
        form = ExhibitSelectForm()

    return render(request, "core/exhibit_select.jinja2", {"form": form})


@require_http_methods(["GET"])
def exhibit(request, slug):
    exhibit = get_object_or_404(Exhibit.objects.prefetch_related("artworks"), slug=slug)
    artworks = exhibit.artworks.select_related("marker", "augmented").all()
    if not artworks:
        raise Http404("No artworks found for this exhibit.")

    ctx = {
        "exhibit": exhibit,
        "artworks": artworks,
    }
    return render(request, "core/exhibit.jinja2", ctx)


@require_http_methods(["GET"])
def related_content(request):
    element_id = request.GET.get("id")
    element_type = request.GET.get("type")
    if element_id is None or element_type is None:
        raise Http404
    if element_type not in ["object", "marker", "artwork", "sound"]:
        raise Http404
    # Bots insert random strings in the id parameter, element_id should be an integer
    try:
        element_id = int(element_id)
    except ValueError:
        raise Http404

    element = None
    ctx = {}
    if element_type in ["object", "marker"]:
        if element_type == "object":
            element = (
                Object.objects.select_related("owner")
                .prefetch_related("artworks__marker")
                .get(id=element_id)
            )
        else:
            element = (
                Marker.objects.select_related("owner")
                .prefetch_related("artworks__augmented")
                .get(id=element_id)
            )

        artworks = element.artworks.all()
        # Get all exhibits that have artworks related to the object or marker
        # Use values_list to get a list of artwork IDs
        # Use distinct to avoid duplicates exhibits
        exhibits = (
            Exhibit.objects.filter(artworks__id__in=element.artworks.values_list("id"))
            .select_related("owner", "owner__user")
            .prefetch_related("artworks")
            .distinct()
        )

        ctx = {"artworks": artworks, "exhibits": exhibits, "seeall:": False}

    elif element_type == "artwork":
        element = Artwork.objects.prefetch_related(
            "exhibits__artworks", "exhibits__owner__user"
        ).get(id=element_id)

        exhibits = element.exhibits.all()

        ctx = {"exhibits": exhibits, "seeall:": False}

    elif element_type == "sound":
        element = Sound.objects.prefetch_related(
            "exhibits", "artworks", "ar_objects"
        ).get(id=element_id)

        ctx = {
            "exhibits": element.exhibits.all(),
            "artworks": element.artworks.all(),
            "objects": element.ar_objects.all(),
            "seeall": False,
        }

    return render(request, COLLECTION_PAGE, ctx)
