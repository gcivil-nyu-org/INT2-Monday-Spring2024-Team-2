from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms.tutor_info import TutorForm, AvailabilityForm
from .forms.student_info import StudentForm
from TutorRegister.models import (
    Expertise,
    Availability,
    ProfileT,
    ProfileS,
    TutoringSession,
)
from django.urls import reverse
from django.http import HttpResponseRedirect
import json
from datetime import datetime, time
from django.db.models import Q
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile


@login_required
def TutorInformation(request):
    initial_availabilities_json = "[]"
    tutor_form = TutorForm()
    existing_expertise = list(
        Expertise.objects.filter(user=request.user).values_list("subject", flat=True)
    )

    if request.method == "POST":
        profile, created = ProfileT.objects.get_or_create(user=request.user)
        tutor_form = TutorForm(request.POST, request.FILES, instance=profile)
        availability_form = AvailabilityForm(request.POST)
        if tutor_form.is_valid() and availability_form.is_valid():
            # save tutor profile data
            user = request.user
            profile = tutor_form.save(commit=False)

            if "image" in request.FILES:
                image = Image.open(request.FILES["image"])

                # Resize the image, preserving aspect ratio
                image.thumbnail((300, 300), Image.Resampling.LANCZOS)

                # Save the resized image to a BytesIO object
                image_io = BytesIO()
                image.save(image_io, format="JPEG")

                # Create a new Django file-like object to save to the model
                image_name = request.FILES["image"].name
                profile.image.save(
                    image_name, ContentFile(image_io.getvalue()), save=False
                )

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
        student_form = StudentForm(request.POST, request.FILES, instance=profile)
        if student_form.is_valid():
            user = request.user
            profile = student_form.save(commit=False)

            if "image" in request.FILES:
                image = Image.open(request.FILES["image"])

                # Resize the image, preserving aspect ratio
                image.thumbnail((300, 300), Image.Resampling.LANCZOS)

                # Save the resized image to a BytesIO object
                image_io = BytesIO()
                image.save(image_io, format="JPEG")

                # Create a new Django file-like object to save to the model
                image_name = request.FILES["image"].name
                profile.image.save(
                    image_name, ContentFile(image_io.getvalue()), save=False
                )
            
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
    context = {"student_form": student_form, "profile": profile}
    return render(request, "Dashboard/student_info.html", context)


@login_required
def StudentDashboard(request):
    return render(request, "Dashboard/student_dashboard.html")


@login_required
def TutorDashboard(request):
    sessions = TutoringSession.objects.filter(
        tutor_id=request.user.id, status="Accepted"
    )
    now = datetime.now()
    upcomingSessions = sessions.filter(
        Q(date__gt=now.date()) | Q(date=now.date(), start_time__gt=now.time())
    )
    pastSessions = sessions.filter(
        Q(date__lt=now.date()) | Q(date=now.date(), start_time__lt=now.time())
    )

    upcomingSessions_studentInfo = []
    pastSessions_studentInfo = []

    for session in upcomingSessions:
        student_profile = ProfileS.objects.get(user=session.student_id)
        upcomingSessions_studentInfo.append((session, student_profile))

    for session in pastSessions:
        student_profile = ProfileS.objects.get(user=session.student_id)
        pastSessions_studentInfo.append((session, student_profile))

    context = {
        "upcomingSessions": upcomingSessions_studentInfo,
        "pastSessions": pastSessions_studentInfo,
    }
    return render(request, "Dashboard/tutor_dashboard.html", context)


def CancelSession(request, session_id):
    session = TutoringSession.objects.get(pk=session_id)
    session.status = "Cancelled"
    session.save()
    return redirect("Dashboard:tutor_dashboard")


def TutorRequest(request):
    tutorRequests = TutoringSession.objects.filter(
        tutor_id=request.user.id, status="Pending"
    )

    tutorRequests_studentInfo = []

    for tutorRequest in tutorRequests:
        student_profile = ProfileS.objects.get(user=tutorRequest.student_id)
        tutorRequests_studentInfo.append((tutorRequest, student_profile))

    context = {"tutorRequests": tutorRequests_studentInfo}
    return render(request, "Dashboard/tutor_request.html", context)


def AcceptRequest(request, session_id):
    session = TutoringSession.objects.get(pk=session_id)
    session.status = "Accepted"
    session.save()
    return redirect("Dashboard:tutor_request")


def DeclineRequest(request, session_id):
    session = TutoringSession.objects.get(pk=session_id)
    session.status = "Rejected"
    session.save()
    return redirect("Dashboard:tutor_request")


def logout_view(request):
    logout(request)
    return redirect("home")


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, time)):
            return obj.strftime("%H:%M")
        return json.JSONEncoder.default(self, obj)
