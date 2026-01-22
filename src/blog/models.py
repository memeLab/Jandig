from django.core.files.storage import default_storage
from django.db import models
from django_extensions.db.models import TimeStampedModel

from users.models import Profile

IMAGE_BASE_PATH = "post_images/"


class PostStatus(models.TextChoices):
    DRAFT = "draft"
    PUBLISHED = "published"


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"


class PostImage(TimeStampedModel):
    file = models.FileField(storage=default_storage, upload_to=IMAGE_BASE_PATH)
    description = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.file.name.lstrip(IMAGE_BASE_PATH)


class Clipping(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    link = models.URLField()
    file = models.FileField(upload_to="clipping_files/")
    display_date = models.DateField(db_index=True)

    def __str__(self):
        return self.title


class Post(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    status = models.CharField(
        choices=PostStatus.choices, max_length=20, default=PostStatus.DRAFT
    )
    author = models.ForeignKey(
        Profile,
        on_delete=models.DO_NOTHING,
        related_name="posts",
        null=True,
        blank=True,
    )
    body = models.TextField()
    categories = models.ManyToManyField(Category, related_name="posts", blank=True)
    images = models.ManyToManyField(PostImage, related_name="posts", blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f"/memories/{self.slug}/"
