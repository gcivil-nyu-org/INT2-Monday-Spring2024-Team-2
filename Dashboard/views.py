from django.shortcuts import render, redirect
from django.db.models.functions import Coalesce
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms.tutor_info import (
    TutorForm,
    AvailabilityForm,
    TutorImageForm,
    TutorTranscriptForm,
)
from django.db.models import Count, F, ExpressionWrapper, FloatField, Value, Case, When
from .forms.student_info import StudentForm, StudentImageForm
from .forms.review_form import TutorReviewForm
from .forms.survey_form import SurveyForm
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
from datetime import datetime, time, date
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
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.csrf import csrf_exempt

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
            tutor_transcript_form = TutorTranscriptForm(
                instance=ProfileT.objects.get(user=request.user)
            )
        except ProfileT.DoesNotExist:
            tutor_image_form = TutorImageForm()
            tutor_transcript_form = TutorTranscriptForm()
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
            tutor_transcript_form = TutorTranscriptForm(
                request.POST, request.FILES, instance=profile
            )
            availability_form = AvailabilityForm(request.POST)
            if (
                tutor_form.is_valid()
                and tutor_image_form.is_valid()
                and tutor_transcript_form.is_valid()
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
                if "transcript" in request.FILES:
                    profile.transcript = request.FILES["transcript"]

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
            "tutor_transcript_form": tutor_transcript_form,  # Add this to the context
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
        Q(date__gt=now.date()) | Q(date=now.date(), end_time__gt=now.time())
    )

    pastSessions = sessions.filter(
        Q(date__lt=now.date()) | Q(date=now.date(), end_time__lt=now.time())
    )
    has_upcomingSessions = upcomingSessions
    has_pastSessions = pastSessions

    page_number1 = request.GET.get("upcoming_page", 1)
    page_number2 = request.GET.get("past_page", 1)

    paginator1 = Paginator(upcomingSessions, 3)
    paginator2 = Paginator(pastSessions, 3)

    try:
        upcomingSessions = paginator1.page(page_number1)
    except PageNotAnInteger:
        upcomingSessions = paginator1.page(1)
    except EmptyPage:
        upcomingSessions = paginator1.page(paginator1.num_pages)

    try:
        pastSessions = paginator2.page(page_number2)
    except PageNotAnInteger:
        pastSessions = paginator2.page(1)
    except EmptyPage:
        pastSessions = paginator2.page(paginator2.num_pages)

    context = {
        "baseTemplate": (
            "Dashboard/base_student.html"
            if userType == "student"
            else "Dashboard/base_tutor.html"
        ),
        "userType": userType,
        "upcomingSessions": upcomingSessions,
        "has_upcomingSessions": has_upcomingSessions,
        "pastSessions": pastSessions,
        "has_pastSessions": has_pastSessions,
        "upcoming_page": page_number1,
        "past_page": page_number2,
    }

    return render(request, "Dashboard/dashboard.html", context)


@login_required
def Survey(request, session_id):
    session = TutoringSession.objects.get(pk=session_id)
    s_id = session.student_id
    t_id = session.tutor_id
    if request.method == "POST":
        form = SurveyForm(request.POST)
        print(form.errors)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.session = session
            survey.reviewer = s_id
            survey.reviewee = t_id
            survey.save()

            session.survey_completed = True
            session.save()
            return redirect("Dashboard:dashboard")

    else:
        form = SurveyForm()
    userType = request.user.usertype.user_type
    context = {
        "baseTemplate": (
            "Dashboard/base_student.html"
            if userType == "student"
            else "Dashboard/base_tutor.html"
        ),
        "userType": userType,
        "form": form,
        "session_id": session_id,
    }
    return render(request, "Dashboard/survey.html", context)


@login_required
def ProvideFeedback(request, session_id):
    session = TutoringSession.objects.get(pk=session_id)

    s_id = session.student_id
    t_id = session.tutor_id

    tutor_profile = get_object_or_404(ProfileT, user=t_id)

    if request.method == "POST":
        form = TutorReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.student_id = s_id
            review.tutor_id = t_id
            review.tutoring_session = session
            review.save()

            session.reviewed_by_student = True
            session.save()
            return redirect("Dashboard:dashboard")
    else:
        form = TutorReviewForm()
    return render(
        request, "Dashboard/feedback.html", {"form": form, "profilet": tutor_profile}
    )


@login_required
def TutorFeedback(request):
    reviews = (
        TutorReview.objects.all()
        .filter(tutor_id=request.user.id)
        .select_related("student_id__profiles")
    )

    has_reviews = reviews
    page = request.GET.get("page")
    paginator = Paginator(reviews, 5)
    try:
        reviews = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        reviews = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results.
        reviews = paginator.page(paginator.num_pages)

    return render(
        request,
        "Dashboard/tutor_feedback.html",
        {"has_reviews": has_reviews, "reviews": reviews},
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
            tutor_id=request.user.id, status="Pending", date__gte=date.today()
        ).select_related("student_id__profiles")
    else:
        tutorRequests = TutoringSession.objects.filter(
            student_id=request.user.id,
            status__in=["Pending", "Declined"],
            date__gte=date.today(),
        ).select_related("tutor_id__profilet")

    has_tutorRequests = tutorRequests
    page = request.GET.get("page")
    paginator = Paginator(tutorRequests, 5)
    try:
        tutorRequests = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        tutorRequests = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results.
        tutorRequests = paginator.page(paginator.num_pages)

    context = {
        "baseTemplate": (
            "Dashboard/base_student.html"
            if userType == "student"
            else "Dashboard/base_tutor.html"
        ),
        "userType": userType,
        "tutorRequests": tutorRequests,
        "has_tutorRequests": has_tutorRequests,
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


@login_required
def download_transcript(request, tutor_id):
    tutor_profile = get_object_or_404(ProfileT, pk=tutor_id)

    if tutor_profile.transcript:
        # Open the file directly from the storage backend
        file = tutor_profile.transcript.open("rb")
        # Create a FileResponse with the file's content
        response = FileResponse(
            file, as_attachment=True, filename=tutor_profile.transcript.name
        )
        # Set the content type to the file's content type, if available
        content_type, _ = mimetypes.guess_type(tutor_profile.transcript.name)
        if content_type:
            response["Content-Type"] = content_type
        return response

    return redirect("Dashboard:tutor_profile")


@csrf_exempt
def VideoCall(request):
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "session":
            sessionId = request.POST.get("sessionID", "")
            request.session["temp"] = sessionId
            print("Session ID:", sessionId)
        elif action == "url":
            url = request.POST.get("url", "")
            sessionId = request.session.get("temp")
            if sessionId:
                session = TutoringSession.objects.get(pk=sessionId)
                session.meeting_link = url
                session.save()
                print("Received URL:", url)
            else:
                print("SessionId not found")

    if request.user.usertype.user_type == "tutor":
        tutor = ProfileT.objects.get(user=request.user)
        fname = tutor.fname
        lname = tutor.lname
    else:
        student = ProfileS.objects.get(user=request.user)
        fname = student.fname
        lname = student.lname
    return render(request, "Dashboard/video_call.html", {"name": fname + " " + lname})


@login_required
def AdminDashboard(request):
    tutors = ProfileT.objects.annotate(
        total_reviewee_count=Count("user__user_reviewee", distinct=True),
        total_true=ExpressionWrapper(
            Case(
                When(
                    total_reviewee_count__gt=0,
                    then=100
                    * (
                        Count(
                            "user__user_reviewee__q1",
                            filter=F("user__user_reviewee__q1"),
                        )
                        + Count(
                            "user__user_reviewee__q2",
                            filter=F("user__user_reviewee__q2"),
                        )
                        + Count(
                            "user__user_reviewee__q3",
                            filter=F("user__user_reviewee__q3"),
                        )
                    )
                    / (3 * Count("user__user_reviewee", distinct=True)),
                ),
                default=Value(0),
            ),
            output_field=FloatField(),
        ),
    ).order_by("id")
    expertise = Expertise.objects.all()
    return render(
        request,
        "Dashboard/admin_dashboard.html",
        {"tutors": tutors, "expertise": expertise},
    )


def UpdateQualification(request):
    if request.method == "POST":
        tutor_id = request.POST.get("tutor_id")
        qualifiction = request.POST.get(f"qualification_{tutor_id}")
        tutor = ProfileT.objects.get(id=tutor_id)
        tutor.qualified = qualifiction == "qualified"
        tutor.save()

        tutor_name = tutor.fname
        tutor_user = tutor.user
        tutor_email = tutor_user.username

        if tutor.qualified:
            html_content = render_to_string(
                "Email/qualification_email.html", {"tutor_name": tutor_name}
            )
        else:
            html_content = render_to_string(
                "Email/unqualify_email.html", {"tutor_name": tutor_name}
            )

        email = EmailMessage(
            "Qualification Updated -- TutorNYU",
            html_content,
            "tutornyuengineeringverify@gmail.com",
            [tutor_email],
        )
        email.content_subtype = "html"
        email.send()

        return HttpResponseRedirect(reverse("Dashboard:admin_dashboard"))

    return render(request, "Dashboard/admin_dashboard.html")
