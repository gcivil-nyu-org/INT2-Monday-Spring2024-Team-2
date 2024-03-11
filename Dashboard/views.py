from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms.tutor_info import TutorForm, AvailabilityForm
from .forms.student_info import StudentForm
from TutorRegister.models import Expertise, Availability, ProfileT, ProfileS
from django.urls import reverse
from django.http import HttpResponseRedirect
import json
from datetime import datetime, time


@login_required
def TutorInformation(request):
    existing_expertise = list(
        Expertise.objects.filter(user=request.user).values_list("subject", flat=True)
    )
    if request.method == "POST":
        profile, created = ProfileT.objects.get_or_create(user=request.user)
        tutor_form = TutorForm(request.POST, instance=profile)
        availability_form = AvailabilityForm(request.POST)
        if tutor_form.is_valid() and availability_form.is_valid():
            # save tutor profile data
            user = request.user
            profile = tutor_form.save(commit=False)
            profile.user = user
            profile.save()

            Availability.objects.filter(user=request.user).delete()
            serialized_availabilities = request.POST.get("availabilities")
            availabilities = json.loads(serialized_availabilities)

            for availability_data in availabilities:
                availability_data["user"] = user
                Availability.objects.create(**availability_data)

            # save expertise data to database
            Expertise.objects.filter(user=request.user).delete()
            selected_expertise = request.POST.getlist("expertise")
            if selected_expertise:
                for expertise in selected_expertise:
                    Expertise.objects.create(user=user, subject=expertise)
            user.usertype.has_profile_complete = True
            user.usertype.save()
            return HttpResponseRedirect(reverse("Dashboard:tutor_dashboard"))
    else:
        profile = None
        existing_availabilities = None
        tutor_form = TutorForm()
        initial_availabilities_json = "[]"
        try:
            profile = ProfileT.objects.get(user=request.user)
            existing_availabilities = Availability.objects.filter(user=request.user)
            initial_availabilities_json = json.dumps(
                list(
                    existing_availabilities.values(
                        "day_of_week", "start_time", "end_time"
                    )
                ),
                cls=DateTimeEncoder,
            )
            tutor_form = TutorForm(instance=profile)
        except Exception as e:
            print("Error " + str(e))
        availability_form = AvailabilityForm()
        tutor_form.initial["expertise"] = existing_expertise
    context = {
        "tutor_form": tutor_form,
        "availability_form": availability_form,
        "initial_availabilities_json": initial_availabilities_json,
    }
    return render(request, "Dashboard/tutor_info.html", context)


@login_required
def StudentInformation(request):
    if request.method == "POST":
        profile, created = ProfileS.objects.get_or_create(user=request.user)
        print(profile)
        student_form = StudentForm(request.POST, instance=profile)
        if student_form.is_valid():
            user = request.user
            profile = student_form.save(commit=False)
            profile.user = user
            profile.save()
            user.usertype.has_profile_complete = True
            user.usertype.save()
            return HttpResponseRedirect(reverse("Dashboard:student_dashboard"))
    else:
        profile = None
        student_form = StudentForm()
        try:
            profile = ProfileS.objects.get(user=request.user)
            student_form = StudentForm(instance=profile)
        except Exception as e:
            print("Error " + str(e))
    context = {"student_form": student_form}
    return render(request, "Dashboard/student_info.html", context)


@login_required
def StudentDashboard(request):
    return render(request, "Dashboard/student_dashboard.html")


@login_required
def TutorDashboard(request):
    return render(request, "Dashboard/tutor_dashboard.html")


def logout_view(request):
    logout(request)
    return redirect("home")


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, time)):
            return obj.strftime("%H:%M")
        return json.JSONEncoder.default(self, obj)
