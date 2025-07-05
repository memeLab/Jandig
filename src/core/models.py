import logging
import re

import pghistory
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from fast_html import a, b, div, h1, img, p, render, video
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
        if editable and not self.in_use:
            return render(
                [
                    self.as_html(height, width),
                    self._get_edit_button(),
                    self._get_delete_button(),
                ]
            )
        return self.as_html(height=height, width=width)


@pghistory.track()
class Object(TimeStampedModel, ContentMixin):
    owner = models.ForeignKey(
        Profile, on_delete=models.DO_NOTHING, related_name="ar_objects"
    )
    source = models.FileField(upload_to="objects/")
    author = models.CharField(max_length=60, blank=False)
    title = models.CharField(max_length=60, default="")
    scale = models.CharField(default="1 1", max_length=50)
    position = models.CharField(default="0 0 0", max_length=50)
    rotation = models.CharField(default="270 0 0", max_length=50)
    # Save the file size of the object, so we avoid making requests to S3 / MinIO to check for it.
    file_size = models.IntegerField(default=0, blank=True, null=True)

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

    @property
    def xproportion(self):
        """
        The 'xproportion' method is used to always reduce scale
        to 1:[something], so that new calculations can be made
        when a new scale value is entered by the user.
        """
        a = re.findall(SCALE_REGEX, self.scale)
        width = float(a[0])
        height = float(a[1])
        if width > height:
            height = (height * 1.0) / width
            width = 1
        else:
            width = (width * 1.0) / height
            height = 1
        return width

    @property
    def yproportion(self):
        """
        The 'yproportion' method is used to always reduce scale
        to 1:[something], so that new calculations can be made
        when a new scale value is entered by the user.
        """
        a = re.findall(SCALE_REGEX, self.scale)
        width = float(a[0])
        height = float(a[1])
        if width > height:
            height = (height * 1.0) / width
            width = 1
        else:
            width = (width * 1.0) / height
            height = 1
        return height

    @property
    def xscale(self):
        """
        The 'xscale' method returns the original proportion
        of the Object multiplied by the scale value entered
        by the user, and thus the Object appears resized in
        augmented reality.
        """
        a = re.findall(SCALE_REGEX, self.scale)
        return a[0]

    @property
    def yscale(self):
        """
        The 'yscale' method returns the original proportion
        of the Object multiplied by the scale value entered
        by the user, and thus the Object appears resized in
        augmented reality.
        """
        a = re.findall(SCALE_REGEX, self.scale)
        return a[1]

    @property
    def fullscale(self):
        """
        The 'fullscale' method is a workaround to show the
        users the last scale value entered by them, when
        they attempt to edit it.
        """
        x = self.xscale
        y = self.yscale
        if x > y:
            return x
        return y

    @property
    def xposition(self):
        x = self.position.split(" ")[0]
        return float(x)

    @property
    def yposition(self):
        y = self.position.split(" ")[1]
        return float(y)

    @property
    def is_video(self):
        """
        checks if the Object is a video by checking the file extension.
        """
        if self.source.name.endswith(".mp4") or self.source.name.endswith(".webm"):
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
        else:
            return render(img(**attributes))

    def as_html_thumbnail(self, editable=False):
        thumbnail_height = DEFAULT_OBJECT_THUMBNAIL_HEIGHT
        thumbnail_width = DEFAULT_OBJECT_THUMBNAIL_WIDTH
        height = thumbnail_height * self.yproportion
        width = thumbnail_width * self.xproportion
        if editable and not self.in_use:
            return render(
                [
                    self.as_html(height, width),
                    self._get_edit_button(),
                    self._get_delete_button(),
                ]
            )
        return self.as_html(height=height, width=width)


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
    title = models.CharField(max_length=50, blank=False)
    description = models.TextField(max_length=500, blank=True)

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
        if editable and not self.in_use:
            elements.extend(
                [
                    self._get_edit_button(),
                    self._get_delete_button(),
                    a(
                        _("preview"),
                        href=reverse("artwork-preview", query={"id": self.id}),
                        class_="preview",
                    ),
                ]
            )
        return render(div(elements, class_="artwork-elements flex"))


@receiver(post_delete, sender=Object)
@receiver(post_delete, sender=Marker)
def remove_source_file(sender, instance, **kwargs):
    instance.source.delete(False)


@pghistory.track()
class Exhibit(TimeStampedModel, ContentMixin, models.Model):
    owner = models.ForeignKey(
        Profile, on_delete=models.DO_NOTHING, related_name="exhibits"
    )
    name = models.CharField(unique=True, max_length=50)
    slug = models.CharField(unique=True, max_length=50)
    artworks = models.ManyToManyField(Artwork, related_name="exhibits")

    def __str__(self):
        return self.name

    @property
    def artworks_count(self):
        return self.artworks.count()

    @property
    def date(self):
        return self.created.strftime("%d/%m/%Y")

    def as_html_thumbnail(self, editable=False):
        link_to_exhibit = reverse("exhibit-detail", query={"id": self.id})
        exhibit_title = a(h1(self.name, class_="exhibit-name"), href=link_to_exhibit)

        exhibit_info = [
            p([{_("Created by ")}, b(self.owner.user.username)], class_="by"),
            p(self.date, class_="exbDate"),
            p(
                a(
                    "{} {}".format(self.artworks_count, _("Artwork(s)")),
                    href=link_to_exhibit,
                ),
                class_="exhibit-about",
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
                [
                    self._get_edit_button(),
                    self._get_delete_button(),
                ]
            )
        exhibit_card = div(div(exhibit_card_elements, class_="exhibit-elements flex"))
        elements = [
            exhibit_title,
            exhibit_card,
        ]
        return render(elements)
