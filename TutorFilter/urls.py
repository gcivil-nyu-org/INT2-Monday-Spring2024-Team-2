from django.urls import path
from . import views

app_name = "TutorFilter"

urlpatterns = [
    path("", views.filter_tutors, name="filter_tutors"),
]
