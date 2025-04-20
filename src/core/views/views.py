from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from core.forms import ExhibitForm, ExhibitSelectForm
from core.models import Artwork, Exhibit, Marker, Object
from users.models import Profile


@require_http_methods(["GET"])
def service_worker(request):
    return render(request, "core/sw.js", content_type="application/x-javascript")


@require_http_methods(["GET"])
def manifest(request):
    return render(
        request, "core/manifest.json", content_type="application/x-javascript"
    )


def index(request):
    ctx = {"artworks": []}

    return render(request, "core/exhibit.jinja2", ctx)


@require_http_methods(["GET"])
def collection(request):
    exhibits = (
        Exhibit.objects.select_related("owner", "owner__user")
        .prefetch_related("artworks")
        .all()
        .order_by("-creation_date")[:4]
    )
    artworks = (
        Artwork.objects.select_related("author", "author__user", "marker", "augmented")
        .all()
        .order_by("-created_at")[:6]
    )
    markers = Marker.objects.all().order_by("-uploaded_at")[:8]
    objects = Object.objects.all().order_by("-uploaded_at")[:8]

    ctx = {
        "artworks": artworks,
        "exhibits": exhibits,
        "markers": markers,
        "objects": objects,
        "seeall": False,
    }

    return render(request, "core/collection.jinja2", ctx)


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


@require_http_methods(["GET"])
def see_all(request, which="", page=1):
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
        "objects": Object.objects.all().order_by("uploaded_at"),
        "markers": Marker.objects.all().order_by("uploaded_at"),
        "artworks": Artwork.objects.prefetch_related("marker", "augmented")
        .all()
        .order_by("created_at"),
        "exhibits": Exhibit.objects.select_related("owner", "owner__user")
        .prefetch_related("artworks")
        .all()
        .order_by("creation_date"),
    }

    data = data_types.get(request_type)
    if data:
        paginator = Paginator(data, per_page)
        if page > paginator.num_pages:
            return redirect("see_all", request_type, paginator.num_pages)
        paginated_data = paginator.get_page(page)
        paginated_data.adjusted_elided_pages = paginator.get_elided_page_range(page)
        ctx = {
            request_type: paginated_data,
            "seeall": True,
        }
    return render(request, "core/collection.jinja2", ctx)


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


@require_http_methods(["GET"])
def artwork_preview(request):
    artwork_id = request.GET.get("id")

    ctx = {
        "artworks": Artwork.objects.filter(id=artwork_id).order_by("-id"),
    }
    return render(request, "core/exhibit.jinja2", ctx)


@require_http_methods(["GET"])
def exhibit(request, slug):
    exhibit = get_object_or_404(Exhibit.objects.prefetch_related("artworks"), slug=slug)
    ctx = {
        "exhibit": exhibit,
        "artworks": exhibit.artworks.select_related("marker", "augmented").all(),
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
        "users/exhibit-create.jinja2",
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
