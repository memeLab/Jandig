from io import BytesIO

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.base import File
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from core.forms import (
    ArtworkForm,
    ExhibitForm,
    ExhibitSelectForm,
    UploadMarkerForm,
    UploadObjectForm,
)
from core.glb_thumbnail_generator import generate_thumbnail
from core.models import Artwork, Exhibit, ExhibitTypes, Marker, Object, ObjectExtensions
from core.utils import generate_uuid_name
from users.models import Profile


@require_http_methods(["GET"])
def collection(request):
    exhibits = (
        Exhibit.objects.select_related("owner", "owner__user")
        .prefetch_related("artworks")
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

    ctx = {
        "artworks": artworks,
        "exhibits": exhibits,
        "markers": markers,
        "objects": objects,
        "seeall": False,
    }

    return render(request, "core/collection.jinja2", ctx)


@require_http_methods(["GET"])
def see_all(request, which=""):
    request_type = request.GET.get("which", which)
    if request_type not in ["objects", "markers", "artworks", "exhibits"]:
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
        "objects": Object.objects.all().order_by("created"),
        "markers": Marker.objects.all().order_by("created"),
        "artworks": Artwork.objects.prefetch_related("marker", "augmented")
        .all()
        .order_by("created"),
        "exhibits": Exhibit.objects.select_related("owner", "owner__user")
        .prefetch_related("artworks")
        .all()
        .order_by("created"),
    }

    data = data_types.get(request_type)
    if data:
        paginator = Paginator(data, per_page)
        if page > paginator.num_pages:
            return redirect("see_all", request_type)
        paginated_data = paginator.get_page(page)
        paginated_data.adjusted_elided_pages = paginator.get_elided_page_range(page)
        ctx = {
            request_type: paginated_data,
            "seeall": True,
        }
    return render(request, "core/collection.jinja2", ctx)


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
    elif content_type == "exhibit":
        delete_content(Exhibit, request.user, request.GET.get("id", -1))
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

            # Generate thumbnail if the file is a GLB
            if obj.file_extension == ObjectExtensions.GLB:
                image = generate_thumbnail(obj)
                # Save the thumbnail image to the object
                thumbnail_name = generate_uuid_name() + ".png"
                blob = BytesIO()
                image.save(blob, format="PNG")
                obj.thumbnail.save(thumbnail_name, File(blob), save=True)
            return redirect("profile")
    else:
        form = UploadObjectForm()

    return render(
        request,
        "core/upload-object.jinja2",
        {"form": form, "edit": False},
    )


@login_required
def marker_upload(request):
    if request.method == "POST":
        form = UploadMarkerForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.owner = request.user.profile
            upload.save()
            return redirect("profile")
    else:
        form = UploadMarkerForm()

    return render(
        request,
        "core/upload-marker.jinja2",
        {"form_type": "marker", "form": form, "route": "marker-upload", "edit": False},
    )


def edit_elements(request, form_class, route, model, model_data):
    if not model or model.owner != Profile.objects.get(user=request.user):
        raise Http404

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=model)

        form.full_clean()
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = form_class(initial=model_data)
    return render(
        request,
        route,
        {
            "form": form,
            "model": model,
            "edit": True,
        },
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

    return edit_elements(
        request,
        UploadMarkerForm,
        route="core/edit-marker.jinja2",
        model=model,
        model_data=model_data,
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
    }
    return edit_elements(
        request,
        UploadObjectForm,
        route="core/upload-object.jinja2",
        model=model,
        model_data=model_data,
    )


def get_element(request, form_class, form_type, source, author, existent_element):
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


@login_required
def create_artwork(request):
    if request.method == "POST":
        form = ArtworkForm(request.POST, request.FILES)

        if form.is_valid():
            selected_marker = form.cleaned_data.get("selected_marker")
            selected_object = form.cleaned_data.get("selected_object")

            marker = Marker.objects.get(id=selected_marker) if selected_marker else None
            augmented = (
                Object.objects.get(id=selected_object) if selected_object else None
            )

            if marker and augmented:
                data = form.cleaned_data
                Artwork(
                    author=request.user.profile,
                    marker=marker,
                    augmented=augmented,
                    title=data["title"],
                    description=data["description"],
                    scale_x=data["scale"],
                    scale_y=data["scale"],
                    position_x=data["position_x"],
                    position_y=data["position_y"],
                ).save()

                return redirect("profile")
    else:
        form = ArtworkForm()

    marker_list = Marker.objects.all().order_by("-created")
    object_list = (
        Object.objects.exclude(file_extension=ObjectExtensions.GLB)
        .all()
        .order_by("-created")
    )

    return render(
        request,
        "core/upload-artwork.jinja2",
        {
            "form": form,
            "marker_list": marker_list,
            "object_list": object_list,
        },
    )


@login_required
def edit_artwork(request):
    index = request.GET.get("id", "-1")
    try:
        model = Artwork.objects.get(id=index)
    except Artwork.DoesNotExist:
        raise Http404
    if model.author != Profile.objects.get(user=request.user):
        raise Http404

    if request.method == "POST":
        form = ArtworkForm(request.POST, request.FILES)

        form.full_clean()
        if form.is_valid():
            selected_marker = form.cleaned_data.get("selected_marker")
            selected_object = form.cleaned_data.get("selected_object")

            marker = Marker.objects.get(id=selected_marker) if selected_marker else None
            augmented = (
                Object.objects.get(id=selected_object) if selected_object else None
            )
            data = form.cleaned_data
            model_data = {
                "marker": marker,
                "augmented": augmented,
                "title": data["title"],
                "description": data["description"],
                "scale_x": data["scale"],
                "scale_y": data["scale"],
                "position_x": data["position_x"],
                "position_y": data["position_y"],
            }
            Artwork.objects.filter(id=model.id).update(**model_data)
            return redirect("profile")

    model = model
    model_data = {
        "marker": model.marker,
        "augmented": model.augmented,
        "title": model.title,
        "description": model.description,
        "selected_marker": model.marker.id,
        "selected_object": model.augmented.id,
        "scale": model.scale_x,
        "position_x": model.position_x,
        "position_y": model.position_y,
    }

    marker_list = Marker.objects.all().order_by("-created")
    object_list = (
        Object.objects.exclude(file_extension=ObjectExtensions.GLB)
        .all()
        .order_by("-created")
    )

    return render(
        request,
        "core/upload-artwork.jinja2",
        {
            "form": ArtworkForm(initial=model_data),
            "marker_list": marker_list,
            "object_list": object_list,
            "selected_marker": model.marker.id,
            "selected_object": model.augmented.id,
        },
    )


@require_http_methods(["GET"])
def artwork_preview(request):
    artwork_id = request.GET.get("id")

    ctx = {
        "artworks": Artwork.objects.filter(id=artwork_id).order_by("-id"),
    }
    return render(request, "core/exhibit.jinja2", ctx)


@login_required
def create_exhibit(request):
    if request.method == "POST":
        form = ExhibitForm(request.POST)
        if form.is_valid():
            _process_exhibit_form_data(form, request.user.profile)
            return redirect("profile")
    else:
        form = ExhibitForm()

    context = _get_exhibit_context_data(request.user.profile, form)
    return render(request, "core/exhibit_create.jinja2", context)


@login_required
def edit_exhibit(request):
    index = request.GET.get("id", "-1")
    try:
        model = Exhibit.objects.get(id=index)
    except Exhibit.DoesNotExist:
        raise Http404

    if model.owner != Profile.objects.get(user=request.user):
        raise Http404

    if request.method == "POST":
        form = ExhibitForm(request.POST, exhibit_id=index)
        form.full_clean()

        if form.is_valid():
            _process_exhibit_form_data(form, request.user.profile, model)
            return redirect("profile")
        else:
            # Form is not valid, render with errors
            model_artworks = ",".join(
                str(artwork.id) for artwork in model.artworks.all()
            )
            context = _get_exhibit_context_data(
                request.user.profile, form, model_artworks, edit=True
            )
            return render(request, "core/exhibit_create.jinja2", context)
    else:
        # GET request - prepare initial form data
        model_artworks = ",".join(str(artwork.id) for artwork in model.artworks.all())
        model_augmenteds = ",".join(
            str(augmented.id) for augmented in model.augmenteds.all()
        )

        model_data = {
            "name": model.name,
            "slug": model.slug,
            "artworks": model_artworks,
            "augmenteds": model_augmenteds,
        }

        form = ExhibitForm(initial=model_data, exhibit_id=index)
        context = _get_exhibit_context_data(
            request.user.profile, form, model_artworks, model_augmenteds, edit=True
        )
        return render(request, "core/exhibit_create.jinja2", context)


def _process_exhibit_form_data(form, user_profile, exhibit=None):
    """Helper method to process exhibit form data and save/update exhibit."""
    selected_artworks = form.cleaned_data.get("artworks", "")
    selected_augmenteds = form.cleaned_data.get("augmenteds", "")

    artwork_ids = selected_artworks.split(",") if selected_artworks else []
    augmenteds_ids = selected_augmenteds.split(",") if selected_augmenteds else []

    artworks = Artwork.objects.filter(id__in=artwork_ids).order_by("-id")
    augmenteds = Object.objects.filter(id__in=augmenteds_ids).order_by("-id")
    exhibit_type = ExhibitTypes.MR if len(augmenteds) > 0 else ExhibitTypes.AR

    if exhibit:
        # Update existing exhibit
        model_data = {
            "name": form.cleaned_data["name"],
            "slug": form.cleaned_data["slug"],
            "exhibit_type": exhibit_type,
        }
        Exhibit.objects.filter(id=exhibit.id).update(**model_data)
        exhibit.artworks.set(artworks)
        exhibit.augmenteds.set(augmenteds)
    else:
        # Create new exhibit
        exhibit = Exhibit(
            owner=user_profile,
            name=form.cleaned_data["name"],
            slug=form.cleaned_data["slug"],
            exhibit_type=exhibit_type,
        )
        exhibit.save()
        exhibit.artworks.set(artworks)
        exhibit.augmenteds.set(augmenteds)


def _get_exhibit_context_data(
    user_profile, form, selected_artworks="", selected_objects="", edit=False
):
    """Helper method to prepare context data for exhibit templates."""
    artworks = Artwork.objects.filter(author=user_profile).order_by("-id")
    objects = Object.objects.all().order_by("-created")

    context = {
        "form": form,
        "artworks": artworks,
        "objects": objects,
    }

    if edit:
        context.update(
            {
                "selected_artworks": selected_artworks,
                "selected_objects": selected_objects,
                "edit": True,
            }
        )

    return context


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
    }
    return render(request, "core/exhibit_detail.jinja2", ctx)


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
    if element_type not in ["object", "marker", "artwork"]:
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

    return render(request, "core/collection.jinja2", ctx)
