# blog/urls.py

from blog import views
from django.urls import path

urlpatterns = [
    path("", views.blog_index, name="blog_index"),
    path("post/<int:pk>/", views.blog_detail, name="blog_detail"),
    path("clippings/", views.clipping, name="clippings"),
    path("category/<category>/", views.blog_category, name="blog_category"),
]
