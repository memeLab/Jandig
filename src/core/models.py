import logging

import pghistory
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from fast_html import a, audio, b, div, h1, img, p, render, span, video
from PIL import Image
from pymarker.core import generate_marker_from_image, generate_patt_from_image

from config.storage_backends import PublicMediaStorage
from users.models import Profile

log = logging.getLogger()

DEFAULT_MARKER_THUMBNAIL_HEIGHT = 50
DEFAULT_MARKER_THUMBNAIL_WIDTH = 50
DEFAULT_OBJECT_THUMBNAIL_HEIGHT = 50
DEFAULT_OBJECT_THUMBNAIL_WIDTH = 50

SCALE_REGEX = r"[\d\.\d]+"


def create_patt(filename, original_filename):
    filestorage = PublicMediaStorage()
    with Image.open(filestorage.open(filename)) as image:
        patt_str = generate_patt_from_image(image)
        patt_file = filestorage.save(
            "patts/" + original_filename + ".patt",
            ContentFile(patt_str.encode("utf-8")),
        )
        return patt_file


def create_marker(filename, original_filename):
    filestorage = PublicMediaStorage()
    with Image.open(filestorage.open(filename)) as image:
        marker_image = generate_marker_from_image(image)
        marker_image.name = original_filename
        marker_image.__commited = False
        return marker_image


class ContentMixin:
    def content_type(self):
        return self.__class__.__name__.lower()

    def _get_edit_button(self):
        content_type = self.content_type()
        return a(
            _("edit"),
            href=reverse(f"edit-{content_type}", query={"id": self.id}),
            class_="edit",
        )

    def _get_delete_button(self):
        content_type = self.content_type()
        return a(
            _("delete"),
            href=reverse(
                "delete-content",
                query={"content_type": content_type, "id": self.id},
            ),
            onclick=f"return confirm('{_('Are you sure you want to delete?')}')",
            class_="delete",
        )

    def used_in_html_string(self):
        used_in = "{} {} {} {} {} {}".format(
            _("Used in"),
            self.artworks_count,
            _("artworks"),
            _("and in "),
            self.exhibits_count,
            _("exhibits"),
        )
        if self.in_use:
            return render(
                a(
                    used_in,
                    href=reverse(
                        "related-content",
                        query={"id": self.id, "type": self.content_type()},
                    ),
                )
            )
        return used_in


class SoundExtensions(models.TextChoices):
    MP3 = "mp3", "MP3"
    OGG = "ogg", "OGG"
    WAV = "wav", "WAV"


@pghistory.track()
class Sound(TimeStampedModel, ContentMixin):
    file = models.FileField(upload_to="sounds/")
    title = models.CharField(max_length=50, blank=False)
    author = models.CharField(max_length=60, blank=False)
    owner = models.ForeignKey(
        Profile, on_delete=models.DO_NOTHING, related_name="sounds"
    )
    # Save the file size of the sound, so we avoid making requests to S3 / MinIO to check for it.
    file_size = models.IntegerField(default=0)
    file_name_original = models.CharField(max_length=255)
    file_extension = models.CharField(
        max_length=10, db_index=True, choices=SoundExtensions.choices
    )

    @property
    def date(self):
        return self.created.strftime("%d/%m/%Y")

    @property
    def artworks_count(self):
        return self.artworks.count()

    @property
    def augmenteds_count(self):
        return self.ar_objects.count()

    @property
    def exhibits_count(self):
        return self.exhibits.count()

    def is_used_by_other_user(self):
        """
        Check if the object is used by another user.
        This is done by checking if there are artworks that reference this object
        and if the owner of those artworks is not the current user.
        """
        return (
            self.ar_objects.exclude(owner=self.owner).exists()
            or self.artworks.exclude(author=self.owner).exists()
            or self.exhibits.exclude(owner=self.owner).exists()
        )

    @property
    def in_use(self):
        if self.exhibits_count > 0:
            return True
        if self.augmenteds_count > 0:
            return True
        if self.artworks_count > 0:
            return True
        return False

    def used_in_html_string(self):
        used_in = "{} {} {} {} {} {} {}".format(
            _("Used in"),
            self.artworks_count,
            _("artworks"),
            self.augmenteds_count,
            _("objects"),
            self.exhibits_count,
            _("exhibits"),
        )

        if self.in_use:
            return render(
                a(
                    used_in,
                    href=reverse(
                        "related-content",
                        query={"id": self.id, "type": self.content_type()},
                    ),
                )
            )
        return used_in

    def as_html(self):
        attributes = {
            "id": self.id,
            "title": self.title,
            "src": self.file.url,
        }
        return render(
            audio(
                **attributes,
                controls=True,
            )
        )

    def as_html_thumbnail(self, editable=False):
        elements = [
            span(self.title, style="display:block;"),
            self.as_html(),
        ]
        if editable and not self.is_used_by_other_user():
            elements.append(self._get_edit_button())

        if editable and not self.in_use:
            elements.append(self._get_delete_button())

        return render(div(elements, style="margin: 10px auto;"))


class ExhibitTypes(models.TextChoices):
    AR = "AR", "Augmented Reality"
    MR = "MR", "Mixed Reality"


@pghistory.track()
class Marker(TimeStampedModel, ContentMixin):
    owner = models.ForeignKey(
        Profile, on_delete=models.DO_NOTHING, related_name="markers"
    )
    source = models.ImageField(upload_to="markers/")
    author = models.CharField(max_length=60, blank=False)
    title = models.CharField(max_length=60, default="")
    patt = models.FileField(upload_to="patts/")

    # Save the file size of the Marker, so we avoid making requests to S3 / MinIO to check for it.
    file_size = models.IntegerField(default=0, blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.source.name

    @property
    def artworks_count(self):
        return self.artworks.count()

    @property
    def artworks_list(self):
        return self.artworks.order_by("-id")

    @property
    def in_use(self):
        if self.artworks_count > 0:
            return True
        return False

    def is_used_by_other_user(self):
        """
        Check if the Marker is used by another user.
        This is done by checking if there are artworks that reference this object
        and if the owner of those artworks is not the current user.
        """
        return self.artworks.exclude(author=self.owner).exists()

    def as_html(self, height: int = None, width: int = None):
        attributes = {
            "id": self.id,
            "title": self.title,
            "src": self.source.url,
        }
        return render(
            img(
                **attributes,
                height=height,
                width=width,
            )
        )

    def as_html_thumbnail(self, editable: bool = False):
        height = DEFAULT_MARKER_THUMBNAIL_HEIGHT
        width = DEFAULT_MARKER_THUMBNAIL_WIDTH
        to_render = [self.as_html(height=height, width=width)]
        # Disabled edit button for now:
        # it only allows to edit the title
        # and it's generating recursive borders on the existing marker.
        # if editable and not self.is_used_by_other_user():
        #     to_render.append(self._get_edit_button())
        if editable and not self.in_use:
            to_render.append(self._get_delete_button())
        return render(to_render)


class ObjectExtensions(models.TextChoices):
    GIF = "gif", "GIF"
    MP4 = "mp4", "MP4"
    WEBM = "webm", "WEBM"
    GLB = "glb", "GLB"


@pghistory.track()
class Object(TimeStampedModel, ContentMixin):
    owner = models.ForeignKey(
        Profile, on_delete=models.DO_NOTHING, related_name="ar_objects"
    )
    sound = models.ForeignKey(
        Sound,
        on_delete=models.DO_NOTHING,
        related_name="ar_objects",
        null=True,
        blank=True,
    )
    audio_description = models.FileField(
        upload_to="audio_descriptions/", null=True, blank=True
    )
    source = models.FileField(upload_to="objects/")
    author = models.CharField(max_length=60, blank=False)
    title = models.CharField(max_length=60, default="")
    # Save the file size of the object, so we avoid making requests to S3 / MinIO to check for it.
    file_size = models.IntegerField(default=0)
    file_name_original = models.CharField(max_length=255)
    file_extension = models.CharField(
        max_length=10, db_index=True, choices=ObjectExtensions.choices
    )
    thumbnail = models.ImageField(
        upload_to="objects/thumbnails/",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.source.name

    @property
    def artworks_count(self):
        return self.artworks.count()

    @property
    def artworks_list(self):
        return self.artworks.order_by("-id")

    @property
    def in_use(self):
        if self.artworks_count > 0:
            return True
        return False

    def is_used_by_other_user(self):
        """
        Check if the object is used by another user.
        This is done by checking if there are artworks that reference this object
        and if the owner of those artworks is not the current user.
        """
        return self.artworks.exclude(author=self.owner).exists()

    @property
    def is_video(self):
        """
        checks if the Object is a video by checking the file extension.
        """
        if self.source.name.endswith(".mp4") or self.source.name.endswith(".webm"):
            return True
        return False

    @property
    def is_3d(self):
        """
        checks if the Object is a 3D model by checking the file extension.
        """
        if self.file_extension in [ObjectExtensions.GLB]:
            return True
        return False

    def as_html(self, height: int = None, width: int = None):
        attributes = {
            "id": self.id,
            "title": self.title,
            "src": self.source.url,
        }
        if height:
            attributes["height"] = height
        if width:
            attributes["width"] = width
        if self.is_video:
            return render(
                video(
                    autoplay=True,
                    loop=True,
                    muted=True,
                    **attributes,
                )
            )
        elif self.is_3d:
            if self.thumbnail:
                attributes["src"] = self.thumbnail.url
            else:
                # Fallback to a placeholder if no thumbnail is available
                attributes["src"] = (
                    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='30' height='30'><rect width='30' height='30' fill='red'/></svg>"
                )
            return render(
                img(
                    **attributes,
                )
            )
        else:
            return render(img(**attributes))

    def as_html_thumbnail(self, editable=False):
        height = DEFAULT_OBJECT_THUMBNAIL_HEIGHT
        width = DEFAULT_OBJECT_THUMBNAIL_WIDTH
        to_render = [self.as_html(height, width)]
        if editable and not self.is_used_by_other_user():
            to_render.append(self._get_edit_button())

        if editable and not self.in_use:
            to_render.append(self._get_delete_button())

        return render(to_render)


@pghistory.track()
class Artwork(TimeStampedModel, ContentMixin):
    author = models.ForeignKey(
        Profile, on_delete=models.DO_NOTHING, related_name="artworks"
    )
    marker = models.ForeignKey(
        Marker, on_delete=models.DO_NOTHING, related_name="artworks"
    )
    augmented = models.ForeignKey(
        Object, on_delete=models.DO_NOTHING, related_name="artworks"
    )
    sound = models.ForeignKey(
        Sound,
        on_delete=models.DO_NOTHING,
        related_name="artworks",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=50, blank=False)
    description = models.TextField(max_length=500, blank=True)
    scale_x = models.FloatField(default=1.0)
    scale_y = models.FloatField(default=1.0)
    position_x = models.FloatField(default=0.0)
    position_y = models.FloatField(default=0.0)

    @property
    def exhibits_count(self):
        return self.exhibits.count()

    @property
    def in_use(self):
        if self.exhibits_count > 0:
            return True

        return False

    def __str__(self):
        return self.title

    def used_in_html_string(self):
        used_in = "{} {} {}".format(
            _("Used in"),
            self.exhibits_count,
            _("Exhibits"),
        )
        if self.in_use:
            return render(
                a(
                    used_in,
                    href=reverse(
                        "related-content",
                        query={"id": self.id, "type": self.content_type()},
                    ),
                )
            )
        return used_in

    def as_html_thumbnail(self, editable=False):
        elements = [
            self.marker.as_html_thumbnail(),
            div(class_="separator"),
            self.augmented.as_html_thumbnail(),
        ]
        if editable:
            elements.extend(
                [
                    self._get_edit_button(),
                ]
            )
            if not self.in_use:
                elements.append(self._get_delete_button())

        if editable:
            elements.extend(
                a(
                    _("preview"),
                    href=reverse("artwork-preview", query={"id": self.id}),
                    class_="preview",
                )
            )
        return render(div(elements, class_="artwork-elements flex"))


@pghistory.track()
class Exhibit(TimeStampedModel, ContentMixin, models.Model):
    owner = models.ForeignKey(
        Profile, on_delete=models.DO_NOTHING, related_name="exhibits"
    )
    name = models.CharField(unique=True, max_length=50)
    slug = models.SlugField(unique=True, max_length=50)
    artworks = models.ManyToManyField(Artwork, related_name="exhibits", blank=True)
    augmenteds = models.ManyToManyField(Object, related_name="exhibits", blank=True)
    sounds = models.ManyToManyField(Sound, related_name="exhibits", blank=True)
    exhibit_type = models.CharField(
        max_length=20,
        choices=[
            (ExhibitTypes.AR, "Augmented Reality"),
            (ExhibitTypes.MR, "Mixed Reality"),
        ],
        default=ExhibitTypes.AR,
        db_index=True,
    )

    def __str__(self):
        return self.name

    @property
    def artworks_count(self):
        return self.artworks.count()

    @property
    def augmenteds_count(self):
        return self.augmenteds.count()

    @property
    def sounds_count(self):
        return self.sounds.count()

    @property
    def date(self):
        return self.created.strftime("%d/%m/%Y")

    def as_html_thumbnail(self, editable=False):
        link_to_exhibit = reverse("exhibit-detail", query={"id": self.id})
        exhibit_title = a(h1(self.name, class_="exhibit-name"), href=link_to_exhibit)

        exhibit_info = [
            p([{_("Created by ")}, b(self.owner.user.username)], class_="by"),
            p(self.date, class_="exbDate"),
            div(
                [
                    p(
                        a(
                            "{} {}".format(self.artworks_count, _("Artwork(s)")),
                            href=link_to_exhibit,
                        ),
                        class_="exhibit-about",
                    ),
                    p(
                        a(
                            "{} {}".format(self.augmenteds_count, _("Object(s)")),
                            href=link_to_exhibit,
                        ),
                        class_="exhibit-about",
                    ),
                    p(
                        a(
                            "{} {}".format(self.sounds_count, _("Sound(s)")),
                            href=link_to_exhibit,
                        ),
                        class_="exhibit-about",
                    ),
                ]
            ),
        ]

        button_see_this_exhibit = a(
            _("See this Exhibition"),
            href=f"/{self.slug}/",
            class_="gotoExb",
        )

        exhibit_card_elements = [
            exhibit_info,
            button_see_this_exhibit,
        ]
        if editable:
            exhibit_card_elements.extend(
                [div([self._get_delete_button(), self._get_edit_button()])]
            )
        exhibit_card = div(div(exhibit_card_elements, class_="exhibit-elements flex"))
        elements = [
            exhibit_title,
            exhibit_card,
        ]
        return render(elements)


@receiver(post_delete, sender=Object)
@receiver(post_delete, sender=Marker)
@receiver(post_delete, sender=Sound)
def remove_source_file(sender, instance, **kwargs):
    if isinstance(instance, Marker):
        instance.source.delete(False)
    if isinstance(instance, Object):
        instance.source.delete(False)
        instance.audio_description.delete(False)
    if isinstance(instance, Sound):
        instance.file.delete(False)
