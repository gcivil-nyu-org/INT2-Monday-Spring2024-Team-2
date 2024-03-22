from django.shortcuts import render, get_object_or_404, redirect
from .forms import TutorFilterForm, TutoringSessionRequestForm
from TutorRegister.models import (
    ProfileT,
    Availability,
    Expertise,
    UserType,
    ProfileS,
    TutoringSession,
)
from django.contrib.auth.models import User
from django.conf import settings
from django.http import JsonResponse
from datetime import datetime, timedelta
import json


def filter_tutors(request):
    form = TutorFilterForm(request.GET)
    users_expertise = Expertise.objects.all()
    users = ProfileT.objects.all()
    has_profile = (
        UserType.objects.all()
        .filter(has_profile_complete=True)
        .values_list("user", flat=True)
    )
    users = users.filter(user__in=has_profile)
    if form.is_valid():
        if form.cleaned_data["expertise"] and form.cleaned_data["expertise"] != "..":
            users_expertise_id = users_expertise.filter(
                subject=form.cleaned_data["expertise"]
            ).values_list("user", flat=True)
            users = users.filter(user__in=users_expertise_id)
        if form.cleaned_data["preferred_mode"]:
            if form.cleaned_data["preferred_mode"] != "..":
                users = users.filter(preferred_mode=form.cleaned_data["preferred_mode"])
        if form.cleaned_data["grade"] and form.cleaned_data["grade"] != "..":
            users = users.filter(grade=form.cleaned_data["grade"])
        if form.cleaned_data["zipcode"] and form.cleaned_data["zipcode"] != "..":
            users = users.filter(zip=form.cleaned_data["zipcode"])
        if form.cleaned_data["salary_max"]:
            users = users
            users = users.filter(salary_min__lt=form.cleaned_data["salary_max"])
    return render(
        request,
        "TutorFilter/filter_results.html",
        {
            "form": form,
            "users": users,
            "MEDIA_URL": settings.MEDIA_URL,
        },
    )


def get_type(user_id):
    u_t = get_object_or_404(UserType, user=user_id)
    t = u_t.user_type

    return t


def view_profile(request, user_id):
    type = get_type(user_id)

    if type == "tutor":
        return view_tutor_profile(request, user_id)

    elif type == "student":
        return view_student_profile(request, user_id)


def view_tutor_profile(request, user_id):
    profilet = get_object_or_404(ProfileT, user=user_id)
    expertise = Expertise.objects.all().filter(user=profilet.user)

    expertises = [get_display_expertise(e.subject) for e in expertise]

    availability = Availability.objects.all().filter(user=profilet.user)
    return render(
        request,
        "TutorFilter/view_tutor_profile.html",
        {
            "profilet": profilet,
            "expertise": expertises,
            "availability": availability,
            "MEDIA_URL": settings.MEDIA_URL,
        },
    )


def view_student_profile(request, user_id):
    profiles = get_object_or_404(ProfileS, user=user_id)

    return render(
        request,
        "TutorFilter/view_student_profile.html",
        {
            "profiles": profiles,
            "MEDIA_URL": settings.MEDIA_URL,
        },
    )


def get_display_expertise(expertise):
    expertise_dict = dict(TutorFilterForm.EXPERTISE_CHOICES)

    return expertise_dict.get(expertise, expertise)


def request_tutoring_session(request, tutor_id):
    tutor_user = get_object_or_404(User, pk=tutor_id)
    tutor_profile = get_object_or_404(ProfileT, user=tutor_user)
    if request.method == "POST":
        form = TutoringSessionRequestForm(request.POST, tutor_user=tutor_user)
        if form.is_valid():
            selected_timeslots = json.loads(
                request.POST.get("selected_timeslots", "[]")
            )
            print(selected_timeslots)
            for timeslot in selected_timeslots:
                print(timeslot)
                tutoring_session = TutoringSession(
                    student_id=request.user,
                    tutor_id=tutor_user,
                    tutoring_mode=form.cleaned_data["tutoring_mode"],
                    subject=form.cleaned_data["subject"],
                    date=form.cleaned_data["date"],
                    start_time=datetime.strptime(timeslot["start"], "%H:%M").time(),
                    end_time=datetime.strptime(timeslot["end"], "%H:%M").time(),
                    offering_rate=form.cleaned_data["offering_rate"],
                    message=form.cleaned_data["message"],
                    status="Pending",
                )
                tutoring_session.save()

            return redirect(
                "Dashboard:student_dashboard",
            )
        else:
            print(form.errors.as_json())
    else:
        form = TutoringSessionRequestForm(tutor_user=tutor_user)
    print(tutor_profile.intro)
    return render(
        request,
        "TutorFilter/request_tutoring_session.html",
        {"form": form, "tutor": tutor_profile},
    )


def get_available_times(request, tutor_id, selected_date):
    if request.method == "POST":
        selected_date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
        day_of_week = selected_date_obj.strftime("%A")
        day = day_of_week
        print("Called get_available_times")
        availabilities = Availability.objects.filter(
            user_id=tutor_id, day_of_week=day.lower()
        )
        booked_sessions = TutoringSession.objects.filter(
            tutor_id=tutor_id, date=selected_date, status="Accepted"
        )
        print(day_of_week)
        print(availabilities)
        available_slots = []
        for availability in availabilities:
            start = datetime.combine(selected_date_obj, availability.start_time)
            end = datetime.combine(selected_date_obj, availability.end_time)

            current = start
            while current < end:
                slot_end = current + timedelta(minutes=30)
                if not booked_sessions.filter(
                    start_time__lt=slot_end.time(), end_time__gt=current.time()
                ).exists():
                    available_slots.append(current.strftime("%H:%M"))
                current = slot_end
        print(available_slots)
        return JsonResponse({"available_slots": available_slots, "day": day.lower()})
