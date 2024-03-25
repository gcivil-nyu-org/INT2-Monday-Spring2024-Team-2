from django.urls import path
from . import views

app_name = "TutorFilter"

urlpatterns = [
    path("", views.filter_tutors, name="filter_tutors"),
    path("profile/<str:user_id>/", views.view_profile, name="view_profile"),
    path("profile/<str:user_id>/", views.view_tutor_profile, name="view_tutor_profile"),
    path(
        "profile/<str:user_id>/",
        views.view_student_profile,
        name="view_student_profile",
    ),
    path("request/<str:tutor_id>/", views.request_tutoring_session, name="request"),
    path(
        "get-available-times/<int:tutor_id>/<str:selected_date>/",
        views.get_available_times,
        name="get-available-times",
    ),
]
