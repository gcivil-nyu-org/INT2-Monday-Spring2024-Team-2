from django.urls import path
from . import views
from .views import (
    CustomPasswordResetView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView,
    CustomPasswordResetDoneView,
)

app_name = "TutorRegister"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("register/success", views.success, name="success"),
    path("register/tutor-information", views.TutorInformation, name="tutorinformation"),
    path(
        "register/student-information",
        views.StudentInformation,
        name="studentinformation",
    ),
    path("login/", views.login_request, name="login"),
    path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path(
        "password_reset/done/",
        CustomPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        CustomPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
