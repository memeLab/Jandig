from django.db import models
from users.models import Profile

class PostStatus(models.TextChoices):
    DRAFT = "draft"
    PUBLISHED = "published"

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"

class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    status = models.CharField(
        choices=PostStatus.choices, max_length=20, default=PostStatus.DRAFT
    )
    author = models.ForeignKey(Profile, on_delete=models.DO_NOTHING, related_name="posts")
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True, editable=True)
    updated = models.DateTimeField(auto_now=True, editable=True)
    categories = models.ManyToManyField(Category, related_name='posts', null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f"/blog/{self.slug}/"
