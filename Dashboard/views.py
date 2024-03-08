from django.shortcuts import render
from .forms.tutor_info import TutorForm, AvailabilityForm
from .forms.student_info import StudentForm
from TutorRegister.models import Expertise, Availability, ProfileT
from django.urls import reverse
from django.http import HttpResponseRedirect
import json
from datetime import datetime, time


# Create your views here.
def TutorInformation(request):
    profile, created = ProfileT.objects.get_or_create(user=request.user)
    existing_expertise = list(
        Expertise.objects.filter(user=request.user).values_list("subject", flat=True)
    )
    if request.method == "POST":
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
            return HttpResponseRedirect(reverse("TutorRegister:success"))
    else:
        profile = ProfileT.objects.get(user=request.user)
        existing_availabilities = Availability.objects.filter(user=request.user)
        # existing_expertise = Expertise.objects.filter(user=request.user).values_list('subject')
        tutor_form = TutorForm(instance=profile)
        initial_availabilities_json = json.dumps(
            list(
                existing_availabilities.values("day_of_week", "start_time", "end_time")
            ),
            cls=DateTimeEncoder,
        )
        availability_form = AvailabilityForm()
        tutor_form.initial["expertise"] = existing_expertise
    context = {
        "tutor_form": tutor_form,
        "availability_form": availability_form,
        "initial_availabilities_json": initial_availabilities_json,
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
            user.usertype.has_profile_complete = True
            user.usertype.save()
            return HttpResponseRedirect(reverse("TutorRegister:success"))
    else:
        form = StudentForm()
    context = {"form": form}
    return render(request, "TutorRegister/student_info.html", context)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, time)):
            return obj.strftime("%H:%M")
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
