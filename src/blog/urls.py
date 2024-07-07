# blog/urls.py

from blog import views
from django.urls import path

urlpatterns = [
    path("", views.blog_index, name="blog_index"),
    path("post/<int:pk>/", views.blog_detail, name="blog_detail"),
    path("clipping/", views.clipping, name="clipping"),
    path("category/<category>/", views.blog_category, name="blog_category"),
]
