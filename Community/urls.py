from django.urls import path
from . import views

app_name = "Community"

urlpatterns = [
    path("", views.view_posts, name="community_posts"),
    path("create-post/", views.create_post, name="create_post"),
]
