from django.urls import path
from . import views


app_name = "Dashboard"

urlpatterns = [
    path("student_profile", views.Student_P_Display, name="studentProfile"),
]
