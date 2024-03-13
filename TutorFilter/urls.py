from django.urls import path
from . import views

app_name = "TutorFilter"

urlpatterns = [
    path("", views.filter_tutors, name="filter_tutors"),
    path('profile/<str:user_id>/', views.view_tutor_profile, name='view_tutor_profile'),
]
