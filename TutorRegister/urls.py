from django.urls import path
from . import views

app_name = "TutorRegister"

urlpatterns = [
    path('register/', views.register, name="register")
]