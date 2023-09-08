from django.urls import path
from core import views

app_name = "core"

urlpatterns = [
    path('', views.index, name="feed"),

    # Ajax URLs
    path("create-post/", views.create_post, name="create-post")

]