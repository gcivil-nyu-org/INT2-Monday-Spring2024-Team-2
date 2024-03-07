from django.urls import path
from . import views

app_name = "Dashboard"

urlpatterns = [
    path("student/edit", views.StudentInformation, name="student_edit"),
    path("tutor/edit", views.TutorInformation, name="tutor_edit"),
]
