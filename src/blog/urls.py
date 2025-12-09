# blog/urls.py

from django.urls import path

from blog import views

urlpatterns = [
    path("", views.blog_index, name="blog_index"),
    path("post/<int:pk>/", views.post_detail, name="post_detail"),
    path("clipping/", views.clipping, name="clipping"),
]
