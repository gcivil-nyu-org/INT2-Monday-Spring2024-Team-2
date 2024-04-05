from django.urls import path
from . import views

app_name = "Dashboard"

urlpatterns = [
    path("", views.UserDashboard, name="dashboard"),
    path("requests", views.Requests, name="requests"),
    path("feedback/", views.TutorFeedback, name="tutor_feedback"),
    path("student/profile", views.StudentInformation, name="student_profile"),
    path("tutor/profile", views.TutorInformation, name="tutor_profile"),
    path("cancel/<int:session_id>/", views.CancelSession, name="cancel_session"),
    path("accept/<int:session_id>/", views.AcceptRequest, name="accept_request"),
    path("decline/<int:session_id>/", views.DeclineRequest, name="decline_request"),
    path("delete/<int:session_id>/", views.DeleteRequest, name="delete_request"),
    path(
        "cancel-request/<int:session_id>/", views.CancelRequest, name="cancel_request"
    ),
    path("logout/", views.logout_view, name="logout"),
    path(
        "download_attachment/<int:session_id>/",
        views.download_attachment,
        name="download_attachment",
    ),
    path(
        "download_transcript/<int:tutor_id>/",
        views.download_transcript,
        name="download_transcript",
    ),
    path("provide-feedback/<int:session_id>/", views.ProvideFeedback, name="feedback"),
    path("videocall/", views.VideoCall, name="video_call"),
]
