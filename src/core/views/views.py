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
    UploadMarkerForm,
    UploadObjectForm,
)
from core.models import Artwork, Exhibit, Marker, Object
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
            "core/upload-marker.jinja2",
            {"form_type": form_type, "form": form, "route": route, "edit": False},
        )

    return render(
        request,
        "core/upload-object.jinja2",
        {"form": form, "route": route, "edit": False},
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

    return render(
        request,
        route,
        {
            "form": form_class(initial=model_data),
            "model": model,
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
        "scale": model.scale.split(" ")[0],
        "position": model.position,
        "rotation": model.rotation,
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


def get_marker(request, form):
    marker_src = form.cleaned_data["marker"]
    marker_author = form.cleaned_data["marker_author"]
    existent_marker = form.cleaned_data["existent_marker"]

    return get_element(
        request,
        UploadMarkerForm,
        Marker,
        source=marker_src,
        author=marker_author,
        existent_element=existent_marker,
    )


def get_augmented(request, form):
    object_src = form.cleaned_data["augmented"]
    object_author = form.cleaned_data["augmented_author"]
    existent_object = form.cleaned_data["existent_object"]

    return get_element(
        request,
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
        "core/upload-artwork.jinja2",
        {
            "form": ArtworkForm(initial=model_data),
            "marker_list": Marker.objects.all(),
            "object_list": Object.objects.all(),
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

    artworks = Artwork.objects.filter(author=request.user.profile).order_by("-id")

    return render(
        request,
        "core/exhibit_create.jinja2",
        {
            "form": form,
            "artworks": artworks,
        },
    )


@login_required
def edit_exhibit(request):
    index = request.GET.get("id", "-1")
    model = Exhibit.objects.filter(id=index)
    if not model or model.first().owner != Profile.objects.get(user=request.user):
        raise Http404

    if request.method == "POST":
        form = ExhibitForm(request.POST, exhibit_id=index)

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
        "core/exhibit_create.jinja2",
        {
            "form": ExhibitForm(initial=model_data, exhibit_id=index),
            "artworks": artworks,
            "selected_artworks": model_artworks,
            "edit": True,
        },
    )


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
    ctx = {
        "exhibit": exhibit,
        "artworks": exhibit.artworks.select_related("marker", "augmented").all(),
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
