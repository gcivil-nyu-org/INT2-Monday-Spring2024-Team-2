from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms.tutor_info import TutorForm, AvailabilityForm, TutorImageForm
from .forms.student_info import StudentForm, StudentImageForm
from .forms.review_form import TutorReviewForm
from TutorRegister.models import (
    Expertise,
    Availability,
    ProfileT,
    ProfileS,
    TutoringSession,
    TutorReview,
)
from django.urls import reverse
from django.http import HttpResponseRedirect
import json
from datetime import datetime, time
from django.db.models import Q
from PIL import Image, ImageDraw, ImageOps
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import FileResponse
from django.shortcuts import get_object_or_404
import mimetypes


@login_required
def TutorInformation(request):
    if request.user.usertype.user_type == "tutor":
        initial_availabilities_json = "[]"
        tutor_form = TutorForm()
        try:
            tutor_image_form = TutorImageForm(
                instance=ProfileT.objects.get(user=request.user)
            )
        except ProfileT.DoesNotExist:
            tutor_image_form = TutorImageForm()
        existing_expertise = list(
            Expertise.objects.filter(user=request.user).values_list(
                "subject", flat=True
            )
        )

        if request.method == "POST":
            profile, created = ProfileT.objects.get_or_create(user=request.user)
            tutor_form = TutorForm(request.POST, instance=profile)
            tutor_image_form = TutorImageForm(
                request.POST, request.FILES, instance=profile
            )
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
                    image = image.resize((300, 300), Image.Resampling.LANCZOS)
                    # Resize and fill with white background
                    new_image = Image.new("RGB", (300, 300), (255, 255, 255))
                    image.thumbnail((300, 300), Image.Resampling.LANCZOS)
                    new_image.paste(
                        image, ((300 - image.width) // 2, (300 - image.height) // 2)
                    )

                    # Crop as a circle
                    mask = Image.new("L", (300, 300), 0)
                    draw = ImageDraw.Draw(mask)
                    draw.ellipse((0, 0, 300, 300), fill=255)
                    circle_image = ImageOps.fit(
                        new_image, (300, 300), centering=(0.5, 0.5)
                    )
                    circle_image.putalpha(mask)

                    # Save the image
                    image_io = BytesIO()
                    circle_image.save(image_io, format="PNG")
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
                return HttpResponseRedirect(reverse("Dashboard:dashboard"))
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

    else:
        return redirect("Dashboard:student_profile")


@login_required
def StudentInformation(request):
    if request.user.usertype.user_type == "student":
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
                    # Resize to 300x300, enlarging if necessary
                    image = image.resize((300, 300), Image.Resampling.LANCZOS)
                    # Fill with white background and crop as a circle
                    new_image = Image.new("RGB", (300, 300), (255, 255, 255))
                    new_image.paste(
                        image, ((300 - image.width) // 2, (300 - image.height) // 2)
                    )
                    mask = Image.new("L", (300, 300), 0)
                    draw = ImageDraw.Draw(mask)
                    draw.ellipse((0, 0, 300, 300), fill=255)
                    new_image.putalpha(mask)
                    # Save the image
                    image_io = BytesIO()
                    new_image.save(image_io, format="PNG")
                    image_name = request.FILES["image"].name
                    profile.image.save(
                        image_name, ContentFile(image_io.getvalue()), save=False
                    )

                profile.user = user
                profile.save()
                user.usertype.has_profile_complete = True
                user.usertype.save()
                return HttpResponseRedirect(reverse("Dashboard:dashboard"))
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

    else:
        return redirect("Dashboard:tutor_profile")


@login_required
def UserDashboard(request):
    userType = request.user.usertype.user_type

    if userType == "student":
        sessions = TutoringSession.objects.filter(
            student_id=request.user.id, status="Accepted"
        ).select_related("tutor_id__profilet")
    else:
        sessions = TutoringSession.objects.filter(
            tutor_id=request.user.id, status="Accepted"
        ).select_related("student_id__profiles")

    now = datetime.now()

    upcomingSessions = sessions.filter(
        Q(date__gt=now.date()) | Q(date=now.date(), start_time__gt=now.time())
    )

    pastSessions = sessions.filter(
        Q(date__lt=now.date()) | Q(date=now.date(), start_time__lt=now.time())
    )

    context = {
        "baseTemplate": (
            "Dashboard/base_student.html"
            if userType == "student"
            else "Dashboard/base_tutor.html"
        ),
        "userType": userType,
        "upcomingSessions": upcomingSessions,
        "pastSessions": pastSessions,
    }

    return render(request, "Dashboard/dashboard.html", context)


@login_required
def ProvideFeedback(request, session_id):
    session = TutoringSession.objects.get(pk=session_id)

    s_id = session.student_id
    t_id = session.tutor_id

    tutor_profile = get_object_or_404(ProfileT, user=t_id)

    if request.method == "POST":
        form = TutorReviewForm(request.POST, s_id=s_id, t_id=t_id)

        if form.is_valid():
            review = form.save(commit=False)
            review.tutoring_session = session
            review.save()
            
            session.reviewed_by_student = True
            session.save()
            return redirect("Dashboard:dashboard")
    else:
        form = TutorReviewForm(s_id=s_id, t_id=t_id)
    return render(
        request, "Dashboard/feedback.html", {"form": form, "profilet": tutor_profile}
    )


@login_required
def CancelSession(request, session_id):
    userType = request.user.usertype.user_type

    session = TutoringSession.objects.get(pk=session_id)

    student = session.student_id
    student_email = student.username
    studentFname = student.first_name
    studentLname = student.last_name

    tutor = session.tutor_id
    tutor_email = tutor.username
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
        [student_email if userType == "tutor" else tutor_email],
    )
    email.content_subtype = "html"
    email.send()

    return redirect("Dashboard:dashboard")


@login_required
def Requests(request):
    userType = request.user.usertype.user_type

    if userType == "tutor":
        tutorRequests = TutoringSession.objects.filter(
            tutor_id=request.user.id, status="Pending"
        ).select_related("student_id__profiles")
    else:
        tutorRequests = TutoringSession.objects.filter(
            student_id=request.user.id, status__in=["Pending", "Declined"]
        ).select_related("tutor_id__profilet")

    context = {
        "baseTemplate": (
            "Dashboard/base_student.html"
            if userType == "student"
            else "Dashboard/base_tutor.html"
        ),
        "userType": userType,
        "tutorRequests": tutorRequests,
    }

    return render(request, "Dashboard/requests.html", context)


def AcceptRequest(request, session_id):
    session = TutoringSession.objects.get(pk=session_id)
    session.status = "Accepted"
    session.save()
    return redirect("Dashboard:requests")


def DeclineRequest(request, session_id):
    session = TutoringSession.objects.get(pk=session_id)
    session.status = "Declined"
    session.save()
    return redirect("Dashboard:requests")


@login_required
def DeleteRequest(request, session_id):
    session = TutoringSession.objects.get(pk=session_id)
    if session.status == "Declined":
        session.delete()

    return redirect("Dashboard:requests")


@login_required
def CancelRequest(request, session_id):
    session = TutoringSession.objects.get(pk=session_id)
    if session.status == "Pending":
        session.status = "Cancelled"
        session.save()

    return redirect("Dashboard:requests")


def logout_view(request):
    logout(request)
    return redirect("home")


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, time)):
            return obj.strftime("%H:%M")
        return json.JSONEncoder.default(self, obj)


@login_required
def download_attachment(request, session_id):
    session = get_object_or_404(TutoringSession, pk=session_id)

    if session.attachment:
        # Open the file directly from the storage backend
        file = session.attachment.open("rb")
        # Create a FileResponse with the file's content
        response = FileResponse(
            file, as_attachment=True, filename=session.attachment.name
        )
        # Set the content type to the file's content type, if available
        content_type, _ = mimetypes.guess_type(session.attachment.name)
        if content_type:
            response["Content-Type"] = content_type
        return response

    return redirect("Dashboard:requests")
