from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms.tutor_info import TutorForm, AvailabilityForm, TutorImageForm
from .forms.student_info import StudentForm, StudentImageForm
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
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.utils import timezone


@login_required
def TutorInformation(request):
    initial_availabilities_json = "[]"
    tutor_form = TutorForm()
    tutor_image_form = TutorImageForm(instance=ProfileT.objects.get(user=request.user))
    existing_expertise = list(
        Expertise.objects.filter(user=request.user).values_list("subject", flat=True)
    )

    if request.method == "POST":
        profile, created = ProfileT.objects.get_or_create(user=request.user)
        tutor_form = TutorForm(request.POST, instance=profile)
        tutor_image_form = TutorImageForm(request.POST, request.FILES, instance=profile)
        availability_form = AvailabilityForm(request.POST)
        if (
            tutor_form.is_valid()
            and tutor_image_form.is_valid()
            and availability_form.is_valid()
        ):
            user = request.user
            profile = tutor_form.save(commit=False)

            # Handle the image field separately using tutor_image_form
            if "image" in request.FILES:
                image = Image.open(request.FILES["image"])
                image.thumbnail((300, 300), Image.Resampling.LANCZOS)
                if image.mode == "RGBA":
                    background = Image.new("RGB", image.size, (255, 255, 255))
                    background.paste(image, (0, 0), image)
                    image = background
                image_io = BytesIO()
                image.save(image_io, format="JPEG")
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

            # Save expertise data to database
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
        "tutor_image_form": tutor_image_form,
        "availability_form": availability_form,
        "initial_availabilities_json": initial_availabilities_json,
    }
    return render(request, "Dashboard/tutor_info.html", context)


@login_required
def StudentInformation(request):
    if request.method == "POST":
        profile, created = ProfileS.objects.get_or_create(user=request.user)
        student_form = StudentForm(request.POST, instance=profile)
        student_image_form = StudentImageForm(
            request.POST, request.FILES, instance=profile
        )

        if student_form.is_valid() and student_image_form.is_valid():
            user = request.user
            profile = student_form.save(commit=False)

            # Handle the image field separately using student_image_form
            if "image" in request.FILES:
                image = Image.open(request.FILES["image"])
                image.thumbnail((300, 300), Image.Resampling.LANCZOS)
                if image.mode == "RGBA":
                    background = Image.new("RGB", image.size, (255, 255, 255))
                    background.paste(image, (0, 0), image)
                    image = background
                image_io = BytesIO()
                image.save(image_io, format="JPEG")
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
        try:
            profile = ProfileS.objects.get(user=request.user)
        except Exception as e:
            print("Error " + str(e))

        student_form = StudentForm(instance=profile)
        student_image_form = StudentImageForm(instance=profile)

    context = {
        "student_form": student_form,
        "student_image_form": student_image_form,
        "profile": profile,
    }
    return render(request, "Dashboard/student_info.html", context)


@login_required
def StudentDashboard(request):
    sessions = TutoringSession.objects.filter(
        student_id=request.user.id,
        status="Accepted"
    ).select_related("tutor_id__profilet")
    
    now = datetime.now()
    
    upcomingSessions = sessions.filter(
        Q(date__gt=now.date()) | Q(date=now.date(), start_time__gt=now.time())
    )
    
    pastSessions = sessions.filter(
        Q(date__lt=now.date()) | Q(date=now.date(), start_time__lt=now.time())
    )
    
    context = {
        "upcomingSessions": upcomingSessions,
        "pastSessions": pastSessions
    }
    
    return render(request, "Dashboard/student_dashboard.html", context)


@login_required
def TutorDashboard(request):
    sessions = TutoringSession.objects.filter(
        tutor_id=request.user.id, status="Accepted"
    )
    now = timezone.now()
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
    student = session.student_id
    student_email = student.username
    print("Student Email:", student_email)
    studentFname = student.first_name
    studentLname = student.last_name

    tutor = session.tutor_id
    tutorFname = tutor.first_name
    tutorLname = tutor.last_name

    sessionDate = session.date
    sessionTime = session.start_time
    session.status = "Cancelled"
    session.save()

    # send email notification to the students about session cancellation
    html_content = render_to_string(
        "Email/cancellation_template.html",
        {
            "studentFname": studentFname,
            "studentLname": studentLname,
            "tutorFname": tutorFname,
            "tutorLname": tutorLname,
            "sessionDate": sessionDate,
            "sessionTime": sessionTime,
        },
    )

    email = EmailMessage(
        "Tutoring Session Cancelled",
        html_content,
        "tutornyuengineeringverify@gmail.com",
        [student_email],
    )
    email.content_subtype = "html"
    email.send()
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
