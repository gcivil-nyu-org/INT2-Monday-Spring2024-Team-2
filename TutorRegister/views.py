from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

from .forms import RegisterUserForm
from .TutorForm import TutorForm
from .StudentForm import StudentForm
# from verify_email.email_handler import send_verification_email


# register.html
def register(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            # user = form.save()
            # inactive_user = send_verification_email(request, form)
            print(form.isTutor)
            # Redirect to a success page or login page
            if form.isTutor():
                return HttpResponseRedirect(reverse("TutorRegister:tutorinformation"))
            elif form.isStudent():
                return HttpResponseRedirect(reverse("TutorRegister:studentinformation"))
        else:
            print("Invalid form")
    else:
        form = RegisterUserForm()
    return render(request, "TutorRegister/register.html", {"form": form})


def TutorInformation(request):
    if request.method == "POST":
        form = TutorForm(request.POST)
        if form.is_valid():
            # Process the form data as needed
            # For example, save to the database
            # user = form.save()
            return render(
                request, "TutorRegister/successful_register.html"
            )  # Redirect to a thank you page or another page
    else:
        form = TutorForm()
    return render(request, "TutorRegister/TutorInformation.html", {"form": form})


def StudentInformation(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            # Process the form data as needed
            # For example, save to the database
            # user = form.save()
            return render(
                request, "TutorRegister/successful_register.html"
            )  # Redirect to a thank you page or another page
    else:
        form = StudentForm()
    return render(request, "TutorRegister/StudentInformation.html", {"form": form})


def success(request):
    return render(request, "TutorRegister/successful_register.html")


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # print(user.usertype.user_type)
                if user.usertype.user_type == "tutor":
                    return render(request, "TutorRegister/tutor_dashboard.html")
                elif user.usertype.user_type == "student":
                    return render(request, "TutorRegister/student_dashboard.html")
                return render(request, "TutorRegister/successful_register.html")
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid email or password.")
    form = AuthenticationForm()
    return render(request, "TutorRegister/login.html", {"login_form": form})
