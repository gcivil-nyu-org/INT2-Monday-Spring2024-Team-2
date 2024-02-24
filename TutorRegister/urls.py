from django.urls import path
from . import views

app_name = "TutorRegister"

urlpatterns = [
    path('tutor/register/', views.register_tutor, name="register_tutor"),
    path('tutor/<int:user_id>/info/', views.tutor_info, name="tutor_info"),
    path('student/register/', views.register_student, name="register_student")
]