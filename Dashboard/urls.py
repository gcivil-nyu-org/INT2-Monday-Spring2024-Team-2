from django.urls import path
from . import views

app_name = "Dashboard"

urlpatterns = [
    path("student", views.StudentDashboard, name="student_dashboard"),
    path("tutor", views.TutorDashboard, name="tutor_dashboard"),
    path("student/edit", views.StudentInformation, name="student_edit"),
    path("tutor/edit", views.TutorInformation, name="tutor_edit"),
    path("logout/", views.logout_view, name="logout"),
]
