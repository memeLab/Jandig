from django.core.files.storage import default_storage
from django.db import models

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


class PostImage(models.Model):
    file = models.FileField(storage=default_storage, upload_to=IMAGE_BASE_PATH)
    description = models.CharField(max_length=500, blank=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name="created")
    modified = models.DateTimeField(auto_now=True, verbose_name="modified")

    class Meta:
        get_latest_by = "modified"
        indexes = [
            models.Index(fields=["-created"], name="postimage_created_desc_idx"),
            models.Index(fields=["-modified"], name="postimage_modified_desc_idx"),
        ]

    def __str__(self):
        return self.file.name.lstrip(IMAGE_BASE_PATH)


class Clipping(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    link = models.URLField()
    file = models.FileField(upload_to="clipping_files/")
    display_date = models.DateField(db_index=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name="created")
    modified = models.DateTimeField(auto_now=True, verbose_name="modified")

    class Meta:
        get_latest_by = "modified"
        indexes = [
            models.Index(fields=["-created"], name="clipping_created_desc_idx"),
            models.Index(fields=["-modified"], name="clipping_modified_desc_idx"),
        ]

    def __str__(self):
        return self.title


class Post(models.Model):
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
    created = models.DateTimeField(auto_now_add=True, verbose_name="created")
    modified = models.DateTimeField(auto_now=True, verbose_name="modified")

    class Meta:
        get_latest_by = "modified"
        indexes = [
            models.Index(fields=["-created"], name="post_created_desc_idx"),
            models.Index(fields=["-modified"], name="post_modified_desc_idx"),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f"/memories/{self.slug}/"
