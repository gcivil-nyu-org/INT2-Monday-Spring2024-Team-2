from django.urls import path
from . import views

app_name = "Community"

urlpatterns = [
    path("all_posts/", views.view_all_posts, name="all_posts"),
    path("<int:post_id>/", views.view_post_detail, name="post_detail"),
    path("create-post/", views.create_post, name="create_post"),
]
