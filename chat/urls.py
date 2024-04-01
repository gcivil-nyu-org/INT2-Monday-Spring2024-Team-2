from django.urls import path
from . import views

app_name = "Chat"

urlpatterns = [
    path("", views.display_chats, name="display_chats"),
    path("<int:other_user_id>/", views.chat_view, name="chat_view"),
]
