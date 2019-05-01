from django.contrib.staticfiles.templatetags.staticfiles import static


def handle_upload_image(image):
    path = "core" + static(f"images/{image.name}")
    with open(path, 'wb+') as destination:
        for chunk in image.chunks():
            destination.write(chunk)
