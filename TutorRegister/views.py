from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    PasswordResetDoneView,
)
from django.urls import reverse_lazy

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

from .forms.register_login import RegisterUserForm
from .forms.tutor_info import TutorForm, AvailabilityForm
from .forms.student_info import StudentForm
from .models import Expertise, Availability, ProfileS

from verify_email.email_handler import send_verification_email
import json


# register.html
def register(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            send_verification_email(request, form)

            # Redirect to a success page or login page
            return HttpResponseRedirect(reverse("TutorRegister:success"))
        else:
            print("Invalid form")
    else:
        form = RegisterUserForm()
    return render(request, "TutorRegister/register.html", {"form": form})


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

                if user.usertype.has_profile_complete:
                    return HttpResponseRedirect(reverse("Dashboard:dashboard"))
                else:
                    if user.usertype.user_type == "tutor":
                        return HttpResponseRedirect(reverse("Dashboard:tutor_profile"))
                    else:
                        return HttpResponseRedirect(
                            reverse("Dashboard:student_profile")
                        )

            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid email or password.")
    form = AuthenticationForm()
    print(request.method)
    return render(request, "TutorRegister/login.html", {"login_form": form})


class CustomPasswordResetView(PasswordResetView):
    email_template_name = "registration/password_reset_email.html"
    success_url = reverse_lazy("TutorRegister:password_reset_done")


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "TutorRegister/registration/password_reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "TutorRegister/registration/password_reset_confirm.html"
    success_url = reverse_lazy("TutorRegister:password_reset_complete")


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "TutorRegister/registration/password_reset_complete.html"
