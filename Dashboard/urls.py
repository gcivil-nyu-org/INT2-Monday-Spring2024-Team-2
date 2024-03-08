from django.urls import path
from . import views

app_name = "Dashboard"

urlpatterns = [
    path("student", views.StudentDashboard, name="student_dashboard"),
    path("tutor", views.TutorDashboard, name="tutor_dashboard"),
    path("student/profile", views.StudentInformation, name="student_profile"),
    path("tutor/profile", views.TutorInformation, name="tutor_profile"),
    path("logout/", views.logout_view, name="logout"),
]
