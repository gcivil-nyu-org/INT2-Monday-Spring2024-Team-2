from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .forms.tutor_info import TutorForm, AvailabilityForm
from .forms.student_info import StudentForm
from TutorRegister.models import Expertise, Availability, ProfileS
from django.urls import reverse
from django.http import HttpResponseRedirect
import json


# Create your views here.
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
            print("In if")
            return HttpResponseRedirect(reverse("TutorRegister:success"))
    else:
        print("In else")
        tutor_form = TutorForm()
        availability_form = AvailabilityForm()
    context = {
        "tutor_form": tutor_form,
        "availability_form": availability_form,
    }
    return render(request, "Dashboard/tutor_info.html", context)


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


def StudentDashboard(request):
    return render(request, "Dashboard/student_dashboard.html")


def TutorDashboard(request):
    return render(request, "Dashboard/tutor_dashboard.html")


def logout_view(request):
    logout(request)
    return redirect("home")
