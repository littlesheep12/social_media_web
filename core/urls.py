from django.urls import path
from core import views

app_name = "core"

urlpatterns = [
    path('', views.index, name="feed"),

    # Ajax URLs
    path("create-post/", views.create_post, name="create-post"),
    path("like-post/", views.like_post, name="like-post"),
    path("comment-post/", views.comment_on_post, name="comment-post"),
    path("like-comment/", views.like_comment, name="like-comment"),
]