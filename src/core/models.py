import logging

import pghistory
from django.core.files.base import ContentFile as CF
from django.db import models
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from fast_html import a, audio, img, render, video

from core.marker_utils import delete_marker_files
from users.models import Profile

log = logging.getLogger()

DEFAULT_MARKER_THUMBNAIL_HEIGHT = 64
DEFAULT_MARKER_THUMBNAIL_WIDTH = 64
DEFAULT_OBJECT_THUMBNAIL_HEIGHT = 64
DEFAULT_OBJECT_THUMBNAIL_WIDTH = 64
DEFAULT_OBJECT_PREVIEW_HEIGHT = 320
DEFAULT_OBJECT_PREVIEW_WIDTH = 320
DEFAULT_MARKER_PREVIEW_HEIGHT = 320
DEFAULT_MARKER_PREVIEW_WIDTH = 320

SCALE_REGEX = r"[\d\.\d]+"

USED_IN = _("Used in")


class ContentMixin:
    def content_type(self):
        return self.__class__.__name__.lower()

    def used_in_html_string(self):
        used_in = "{} {} {} {} {} {}".format(
            USED_IN,
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
    in_use = models.BooleanField(default=False)
    is_used_by_other_user = models.BooleanField(default=False)

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



    def used_in_html_string(self):
        used_in = "{} {} {} {} {} {} {}".format(
            USED_IN,
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


class ExhibitTypes(models.TextChoices):
    AR = "AR", "Augmented Reality"
    MR = "MR", "Mixed Reality"


@pghistory.track()
class Marker(TimeStampedModel, ContentMixin):
    owner = models.ForeignKey(
        Profile, on_delete=models.DO_NOTHING, related_name="markers"
    )
    source = models.ImageField(upload_to="markers/")
    marker_img = models.ImageField(upload_to="markers/", blank=True)
    print_img = models.ImageField(upload_to="markers/", blank=True)
    thumb_img = models.ImageField(upload_to="markers/", blank=True)
    author = models.CharField(max_length=60, blank=False)
    title = models.CharField(max_length=60, default="")

    # Save the file size of the Marker, so we avoid making requests to S3 / MinIO to check for it.
    file_size = models.IntegerField(default=0, blank=True, null=True)
    in_use = models.BooleanField(default=False)
    is_used_by_other_user = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.source.name

    @property
    def artworks_count(self):
        return self.artworks.count()

    def as_html(
        self,
        height: int = DEFAULT_MARKER_PREVIEW_HEIGHT,
        width: int = DEFAULT_MARKER_PREVIEW_WIDTH,
        thumbnail: bool = False,
    ):
        image = self.thumb_img if thumbnail else self.print_img
        src = image.url + f"?v={int(self.modified.timestamp())}"
        attributes = {
            "id": self.id,
            "title": self.title,
            "src": src,
        }
        return render(
            img(
                **attributes,
                height=height,
                width=width,
            )
        )


class ObjectExtensions(models.TextChoices):
    GIF = "gif", "GIF"
    PNG = "png", "PNG"
    MP4 = "mp4", "MP4"
    WEBM = "webm", "WEBM"
    GLB = "glb", "GLB"


def object_source_path(instance, filename):
    """Upload path: objects/<id>/source.<ext>"""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return f"objects/{instance.pk}/source.{ext}"


def object_audio_description_path(instance, filename):
    """Upload path: objects/<id>/audio_description.<ext>"""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return f"objects/{instance.pk}/audio_description.{ext}"


def object_thumbnail_path(instance, filename):
    """Upload path: objects/<id>/thumbnail.png"""
    return f"objects/{instance.pk}/thumbnail.png"


def object_spritesheet_path(instance, filename):
    """Upload path: objects/<id>/spritesheet.png"""
    return f"objects/{instance.pk}/spritesheet.png"


def object_spritesheet_metadata_path(instance, filename):
    """Upload path: objects/<id>/metadata.json"""
    return f"objects/{instance.pk}/metadata.json"


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
        upload_to=object_audio_description_path, null=True, blank=True
    )
    source = models.FileField(upload_to=object_source_path)
    author = models.CharField(max_length=60, blank=False)
    title = models.CharField(max_length=60, default="")
    # Save the file size of the object, so we avoid making requests to S3 / MinIO to check for it.
    file_size = models.IntegerField(default=0)
    file_name_original = models.CharField(max_length=255)
    file_extension = models.CharField(
        max_length=10, db_index=True, choices=ObjectExtensions.choices
    )
    in_use = models.BooleanField(default=False)
    is_used_by_other_user = models.BooleanField(default=False)
    thumbnail = models.ImageField(
        upload_to=object_thumbnail_path,
        blank=True,
        null=True,
    )
    spritesheet_file = models.FileField(
        upload_to=object_spritesheet_path,
        blank=True,
        null=True,
    )
    spritesheet_metadata = models.FileField(
        upload_to=object_spritesheet_metadata_path,
        blank=True,
        null=True,
    )
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.source.name

    def relocate_files(self):
        """Move all files to the canonical objects/<pk>/ folder.

        Called after initial save (when pk is available) to ensure files
        live at their ID-based path. Safe to call multiple times — skips
        files that are already in the correct location.

        Also cleans up stale files from previous uploads (e.g. source.webm
        when the new file is source.glb).
        """

        storage = self.source.storage
        changed = False

        def _cleanup_stale(keep_path, prefix):
            """Delete files matching prefix.* in the object folder, except keep_path."""
            folder = f"objects/{self.pk}"
            try:
                _, files = storage.listdir(folder)
            except Exception:
                return
            base = prefix  # e.g. "source"
            for f in files:
                if f.split(".")[0] == base:
                    full_path = f"{folder}/{f}"
                    if full_path != keep_path:
                        try:
                            storage.delete(full_path)
                        except Exception:
                            pass

        def _move(field, target_path):
            nonlocal changed
            if not field.name:
                return
            if field.name == target_path:
                return
            content = field.read()
            field.close()
            old_path = field.name
            try:
                if storage.exists(old_path):
                    storage.delete(old_path)
            except Exception:
                pass
            try:
                if storage.exists(target_path):
                    storage.delete(target_path)
            except Exception:
                pass
            storage.save(target_path, CF(content))
            field.name = target_path
            changed = True

        # Source file
        ext = (
            self.source.name.rsplit(".", 1)[-1].lower()
            if "." in self.source.name
            else ""
        )
        source_target = f"objects/{self.pk}/source.{ext}"
        _move(self.source, source_target)
        _cleanup_stale(source_target, "source")

        # Audio description
        if self.audio_description:
            ad_ext = (
                self.audio_description.name.rsplit(".", 1)[-1].lower()
                if "." in self.audio_description.name
                else ""
            )
            ad_target = f"objects/{self.pk}/audio_description.{ad_ext}"
            _move(self.audio_description, ad_target)
            _cleanup_stale(ad_target, "audio_description")
        else:
            _cleanup_stale(None, "audio_description")

        # Thumbnail — only GLB objects have thumbnails
        if self.thumbnail:
            _move(self.thumbnail, f"objects/{self.pk}/thumbnail.png")
        else:
            _cleanup_stale(None, "thumbnail")

        # Spritesheet — only GIF objects have spritesheets
        if self.spritesheet_file:
            _move(self.spritesheet_file, f"objects/{self.pk}/spritesheet.png")
        else:
            _cleanup_stale(None, "spritesheet")

        # Metadata — only GIF objects have metadata
        if self.spritesheet_metadata:
            _move(self.spritesheet_metadata, f"objects/{self.pk}/metadata.json")
        else:
            _cleanup_stale(None, "metadata")

        if changed:
            self.save()

    @property
    def artworks_count(self):
        return self.artworks.count()

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
        max_w = width if width else DEFAULT_OBJECT_PREVIEW_WIDTH
        max_h = height if height else DEFAULT_OBJECT_PREVIEW_HEIGHT

        if self.width and self.height:
            ratio = min(max_w / self.width, max_h / self.height)
            attributes["width"] = int(self.width * ratio)
            attributes["height"] = int(self.height * ratio)
        else:
            attributes["width"] = max_w
            attributes["height"] = max_h

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
            USED_IN,
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

    def content_type(self):
        if self.exhibit_type == ExhibitTypes.AR:
            return "ar-exhibit"
        elif self.exhibit_type == ExhibitTypes.MR:
            return "mr-exhibit"
        else:
            raise ValueError("Invalid exhibit type")


@receiver(post_delete, sender=Object)
@receiver(post_delete, sender=Marker)
@receiver(post_delete, sender=Sound)
def remove_source_file(sender, instance, **kwargs):
    if isinstance(instance, Marker):
        delete_marker_files(instance)
    if isinstance(instance, Object):
        instance.source.delete(False)
        # audio_description is FileField(null=True, blank=True). An Object
        # created without one can surface as None here (or as a FieldFile
        # with an empty name), and calling .delete() on that raises
        # AttributeError and aborts the rest of the cleanup, orphaning the
        # source file we just removed. See #849.
        if instance.audio_description:
            instance.audio_description.delete(False)
        if instance.spritesheet_file:
            instance.spritesheet_file.delete(False)
        if instance.spritesheet_metadata:
            instance.spritesheet_metadata.delete(False)
    if isinstance(instance, Sound):
        instance.file.delete(False)


@receiver(pre_save, sender=Artwork)
def artwork_pre_save(sender, instance, **kwargs):
    """Capture the previous marker/object/sound before an artwork is updated."""
    if not instance.pk:
        return
    try:
        old = Artwork.objects.get(pk=instance.pk)
    except Artwork.DoesNotExist:
        return
    instance._old_marker_id = old.marker_id
    instance._old_augmented_id = old.augmented_id
    instance._old_sound_id = old.sound_id


@receiver(post_save, sender=Artwork)
def artwork_post_save(sender, instance, **kwargs):
    """Mark the current marker/object/sound as in_use; check if old ones are still used."""
    # Mark current references as in use
    Marker.objects.filter(pk=instance.marker_id, in_use=False).update(in_use=True)
    Object.objects.filter(pk=instance.augmented_id, in_use=False).update(in_use=True)
    if instance.sound_id:
        Sound.objects.filter(pk=instance.sound_id, in_use=False).update(in_use=True)

    # Update is_used_by_other_user for current marker/object
    marker = Marker.objects.get(pk=instance.marker_id)
    if instance.author_id != marker.owner_id:
        if not marker.is_used_by_other_user:
            Marker.objects.filter(pk=marker.pk).update(is_used_by_other_user=True)

    augmented = Object.objects.get(pk=instance.augmented_id)
    if instance.author_id != augmented.owner_id:
        if not augmented.is_used_by_other_user:
            Object.objects.filter(pk=augmented.pk).update(is_used_by_other_user=True)

    # Update is_used_by_other_user for current sound
    if instance.sound_id:
        sound = Sound.objects.get(pk=instance.sound_id)
        if instance.author_id != sound.owner_id:
            if not sound.is_used_by_other_user:
                Sound.objects.filter(pk=sound.pk).update(is_used_by_other_user=True)

    # If marker changed, check if the old one is still in use
    old_marker_id = getattr(instance, "_old_marker_id", None)
    if old_marker_id and old_marker_id != instance.marker_id:
        if not Artwork.objects.filter(marker_id=old_marker_id).exists():
            Marker.objects.filter(pk=old_marker_id).update(in_use=False, is_used_by_other_user=False)
        else:
            old_marker = Marker.objects.get(pk=old_marker_id)
            still_used_by_other = old_marker.artworks.exclude(author=old_marker.owner).exists()
            if not still_used_by_other:
                Marker.objects.filter(pk=old_marker_id).update(is_used_by_other_user=False)

    # If object changed, check if the old one is still in use
    old_augmented_id = getattr(instance, "_old_augmented_id", None)
    if old_augmented_id and old_augmented_id != instance.augmented_id:
        if not Artwork.objects.filter(augmented_id=old_augmented_id).exists():
            Object.objects.filter(pk=old_augmented_id).update(in_use=False, is_used_by_other_user=False)
        else:
            old_object = Object.objects.get(pk=old_augmented_id)
            still_used_by_other = old_object.artworks.exclude(author=old_object.owner).exists()
            if not still_used_by_other:
                Object.objects.filter(pk=old_augmented_id).update(is_used_by_other_user=False)

    # If sound changed, check if the old one is still in use
    old_sound_id = getattr(instance, "_old_sound_id", None)
    if old_sound_id and old_sound_id != instance.sound_id:
        _recalculate_sound_flags(old_sound_id)


@receiver(post_delete, sender=Artwork)
def artwork_post_delete(sender, instance, **kwargs):
    """When an artwork is deleted, check if its marker/object/sound are still in use."""
    if not Artwork.objects.filter(marker_id=instance.marker_id).exists():
        Marker.objects.filter(pk=instance.marker_id).update(in_use=False, is_used_by_other_user=False)
    else:
        marker = Marker.objects.get(pk=instance.marker_id)
        if not marker.artworks.exclude(author=marker.owner).exists():
            Marker.objects.filter(pk=marker.pk).update(is_used_by_other_user=False)

    if not Artwork.objects.filter(augmented_id=instance.augmented_id).exists():
        Object.objects.filter(pk=instance.augmented_id).update(in_use=False, is_used_by_other_user=False)
    else:
        obj = Object.objects.get(pk=instance.augmented_id)
        if not obj.artworks.exclude(author=obj.owner).exists():
            Object.objects.filter(pk=obj.pk).update(is_used_by_other_user=False)

    if instance.sound_id:
        _recalculate_sound_flags(instance.sound_id)


def _recalculate_sound_flags(sound_id):
    """Recalculate in_use and is_used_by_other_user for a Sound."""
    try:
        sound = Sound.objects.get(pk=sound_id)
    except Sound.DoesNotExist:
        return

    is_in_use = (
        sound.artworks.exists()
        or sound.ar_objects.exists()
        or sound.exhibits.exists()
    )
    used_by_other = (
        sound.artworks.exclude(author=sound.owner).exists()
        or sound.ar_objects.exclude(owner=sound.owner).exists()
        or sound.exhibits.exclude(owner=sound.owner).exists()
    )
    Sound.objects.filter(pk=sound_id).update(
        in_use=is_in_use, is_used_by_other_user=used_by_other
    )


@receiver(pre_save, sender=Object)
def object_pre_save(sender, instance, **kwargs):
    """Capture the previous sound before an object is updated."""
    if not instance.pk:
        return
    try:
        old = Object.objects.get(pk=instance.pk)
    except Object.DoesNotExist:
        return
    instance._old_sound_id = old.sound_id


@receiver(post_save, sender=Object)
def object_post_save(sender, instance, **kwargs):
    """Update sound flags when an object's sound FK changes."""
    if instance.sound_id:
        sound = Sound.objects.get(pk=instance.sound_id)
        updates = {}
        if not sound.in_use:
            updates["in_use"] = True
        if instance.owner_id != sound.owner_id and not sound.is_used_by_other_user:
            updates["is_used_by_other_user"] = True
        if updates:
            Sound.objects.filter(pk=sound.pk).update(**updates)

    old_sound_id = getattr(instance, "_old_sound_id", None)
    if old_sound_id and old_sound_id != instance.sound_id:
        _recalculate_sound_flags(old_sound_id)


@receiver(post_delete, sender=Object)
def object_post_delete_sound(sender, instance, **kwargs):
    """When an object is deleted, recalculate its sound's flags."""
    if instance.sound_id:
        _recalculate_sound_flags(instance.sound_id)


@receiver(m2m_changed, sender=Exhibit.sounds.through)
def exhibit_sounds_changed(sender, instance, action, pk_set, **kwargs):
    """Update sound flags when exhibits add/remove sounds."""
    if action in ("post_add", "post_remove", "post_clear"):
        if pk_set:
            for sound_id in pk_set:
                _recalculate_sound_flags(sound_id)
        elif action == "post_clear":
            # post_clear doesn't provide pk_set; recalculate all sounds
            for sound in Sound.objects.filter(in_use=True):
                _recalculate_sound_flags(sound.pk)
