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
            user = form.save()
            print(user.username)
            user.usertype.has_profile_complete = False
            user.usertype.save()
            send_verification_email(request, form)

            # Redirect to a success page or login page
            return HttpResponseRedirect(reverse("TutorRegister:success"))
        else:
            print("Invalid form")
    else:
        form = RegisterUserForm()
    return render(request, "TutorRegister/register.html", {"form": form})


def TutorInformation(request):
    if request.method == "POST":
        tutor_form = TutorForm(request.POST)
        availability_form = AvailabilityForm(request.POST)
        if tutor_form.is_valid() and availability_form.is_valid():
            # save tutor profile data
            user = request.user
            profile = tutor_form.save(commit=False)
            profile.user = user
            profile.save()

            # save availability data
            serialized_availabilities = request.POST.get("availabilities")
            availabilities = json.loads(serialized_availabilities)

            for availability_data in availabilities:
                availability_data["user"] = user
                Availability.objects.create(**availability_data)

            # save expertise data to database
            selected_expertise = request.POST.getlist("expertise")
            if selected_expertise:
                for expertise in selected_expertise:
                    Expertise.objects.create(user=user, subject=expertise)
            return HttpResponseRedirect(reverse("TutorRegister:success"))
    else:
        tutor_form = TutorForm()
        availability_form = AvailabilityForm()
    context = {
        "tutor_form": tutor_form,
        "availability_form": availability_form,
    }
    return render(request, "TutorRegister/tutor_info.html", context)


def StudentInformation(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            user = request.user
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            return HttpResponseRedirect(reverse("TutorRegister:success"))
    else:
        form = StudentForm()
    context = {"form": form}
    return render(request, "TutorRegister/student_info.html", context)


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

                if user.usertype.user_type == "tutor":
                    if user.usertype.has_profile_complete:
                        return HttpResponseRedirect(reverse("Dashboard:tutor"))
                    else:
                        return HttpResponseRedirect(reverse("Dashboard:tutor_edit"))
                elif user.usertype.user_type == "student":
                    if user.usertype.has_profile_complete:
                        return HttpResponseRedirect(reverse("Dashboard:student"))
                    else:
                        return HttpResponseRedirect(reverse("Dashboard:student_edit"))
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid email or password.")
    form = AuthenticationForm()
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
