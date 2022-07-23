from django.templatetags.static import static

from django.core.files.storage import default_storage


def handle_upload_image(image):
    path = "core" + static(f"images/{image.name}")
    with open(path, "wb+") as destination:
        for chunk in image.chunks():
            destination.write(chunk)


def handle_upload_patt(patt):
    path = "core" + static(f"patts/{patt.name}")
    with default_storage.open(path, "wb") as destination:
        for chunk in patt.chunks():
            destination.write(chunk)


def handle_upload_marker(image):
    path = "core" + static(f"markers/{image.name}")
    with open(path, "wb+") as destination:
        for chunk in image.chunks():
            destination.write(chunk)
