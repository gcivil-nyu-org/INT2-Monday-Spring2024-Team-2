from django.urls import path
from . import views

app_name = "Community"

urlpatterns = [
    path("", views.view_all_posts, name="all_posts"),
    path("<int:post_id>/", views.view_post_detail, name="post_detail"),
    path("<int:post_id>/edit/", views.edit, name="edit"),
    path("create-post/", views.create_post, name="create_post"),
    path("<int:post_id>/vote/<str:vote_type>/", views.vote, name="vote"),
    path("<int:post_id>/delete", views.delete_post, name="delete_post"),
]
