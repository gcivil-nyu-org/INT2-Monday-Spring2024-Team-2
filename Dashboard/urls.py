from django.urls import path
from . import views

app_name = "Dashboard"

urlpatterns = [
    path("", views.UserDashboard, name="dashboard"),
    path("requests", views.Requests, name="requests"),
    path("student", views.StudentDashboard, name="student_dashboard"),
    path("tutor", views.TutorDashboard, name="tutor_dashboard"),
    path("student/profile", views.StudentInformation, name="student_profile"),
    path("tutor/profile", views.TutorInformation, name="tutor_profile"),
    path("tutor/request", views.TutorRequest, name="tutor_request"),
    path("cancel/<int:session_id>/", views.CancelSession, name="cancel_session"),
    path("accept/<int:session_id>/", views.AcceptRequest, name="accept_request"),
    path("decline/<int:session_id>/", views.DeclineRequest, name="decline_request"),
    path("delete/<int:session_id>/", views.DeleteRequest, name="delete_request"),
    path("cancel-request/<int:session_id>/", views.CancelRequest, name="cancel_request"),
    path("logout/", views.logout_view, name="logout")
]
