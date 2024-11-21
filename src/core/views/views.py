from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods

from core.forms import ExhibitForm, UploadFileForm
from core.helpers import handle_upload_image
from core.models import Artwork, Exhibit, Marker, Object


@cache_page(60 * 60)
@require_http_methods(["GET"])
def service_worker(request):
    return render(request, "core/sw.js", content_type="application/x-javascript")


@cache_page(60 * 60)
@require_http_methods(["GET"])
def manifest(request):
    return render(
        request, "core/manifest.json", content_type="application/x-javascript"
    )


def index(request):
    ctx = {"artworks": []}

    return render(request, "core/exhibit.jinja2", ctx)


@cache_page(60 * 2)
@require_http_methods(["GET"])
def collection(request):
    exhibits = Exhibit.objects.all().order_by("creation_date")[:4]
    artworks = Artwork.objects.all().order_by("created_at")[:6]
    markers = Marker.objects.all().order_by("uploaded_at")[:8]
    objects = Object.objects.all().order_by("uploaded_at")[:8]

    ctx = {
        "artworks": artworks,
        "exhibits": exhibits,
        "markers": markers,
        "objects": objects,
        "seeall": False,
    }

    return render(request, "core/collection.jinja2", ctx)


@cache_page(60 * 2)
@require_http_methods(["GET"])
def see_all(request, which="", page=1):
    request_type = request.GET.get("which", which)
    if request_type not in ["objects", "markers", "artworks", "exhibits"]:
        # Invalid request type, return to collection
        return redirect("collection")
    ctx = {}
    per_page = 3
    page = request.GET.get("page", 1)

    try:
        # Bots insert random strings in the page parameter
        page = int(page)
    except ValueError:
        page = 1

    data_types = {
        "objects": Object.objects.all().order_by("uploaded_at"),
        "markers": Marker.objects.all().order_by("uploaded_at"),
        "artworks": Artwork.objects.all().order_by("created_at"),
        "exhibits": Exhibit.objects.all().order_by("creation_date"),
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


def upload_image(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        image = request.FILES.get("file")
        if form.is_valid() and image:
            handle_upload_image(image)
            return HttpResponseRedirect(reverse("index"))
    else:
        form = UploadFileForm()
    return render(request, "core/upload.jinja2", {"form": form})


def exhibit_select(request):
    if request.method == "POST":
        form = ExhibitForm(request.POST)
        if form.is_valid():
            exhibit = form.cleaned_data.get("exhibit")
            return redirect("/" + exhibit.slug)
    else:
        form = ExhibitForm()

    return render(request, "core/exhibit_select.jinja2", {"form": form})


@cache_page(60 * 60)
@require_http_methods(["GET"])
def exhibit_detail(request):
    index = request.GET.get("id")
    exhibit = Exhibit.objects.get(id=index)
    ctx = {
        "exhibit": exhibit,
        "exhibitImage": "https://cdn3.iconfinder.com/data/icons/basic-mobile-part-2/512/painter-512.png",
        "artworks": exhibit.artworks.all(),
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
