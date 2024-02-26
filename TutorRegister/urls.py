from django.urls import path
from . import views

app_name = "TutorRegister"

urlpatterns = [
    path('register/', views.register, name="register"),
    path('register/success', views.success, name="success"),
    path('register/tutor-information', views.TutorInformation, name='tutorinformation'),
    path('register/student-information', views.StudentInformation, name='studentinformation'),
    path('login/', views.login_request, name='login'),
]