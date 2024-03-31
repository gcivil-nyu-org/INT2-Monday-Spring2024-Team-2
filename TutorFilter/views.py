from django.shortcuts import render, get_object_or_404, redirect
from .forms import TutorFilterForm, TutoringSessionRequestForm
from TutorRegister.models import (
    ProfileT,
    Availability,
    Expertise,
    UserType,
    ProfileS,
    TutoringSession,
    TutorReview,
    Favorite,
)
from django.contrib.auth.models import User
from django.conf import settings
from django.http import JsonResponse
from datetime import datetime, timedelta
import json
from django.db.models import Avg


def filter_tutors(request):
    form = TutorFilterForm(request.GET, user=request.user)
    users_expertise = Expertise.objects.all()
    users = ProfileT.objects.all()
    favorites = Favorite.objects.all().filter(student=request.user)
    tutor_ratings = {user.id: 0.0 for user in users}  # Default rating is 0
    average_ratings = TutorReview.objects.values("tutor_id").annotate(
        average_rating=Avg("rating")
    )
    for rating in average_ratings:
        tutor_ratings[rating["tutor_id"]] = round(rating["average_rating"], 1)

    has_profile = (
        UserType.objects.all()
        .filter(has_profile_complete=True)
        .values_list("user", flat=True)
    )
    users = users.filter(user__in=has_profile)

    # users.sort(key=lambda x: sorted_tutors_ids.index(x.id))

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
            users = users.filter(salary_min__lt=form.cleaned_data["salary_max"])
        if form.cleaned_data["rating"]:
            if form.cleaned_data["rating"] == ">= 1 star":
                high_rating_tutors = {
                    user: rating
                    for user, rating in tutor_ratings.items()
                    if rating >= 1
                }
                users = users.filter(id__in=high_rating_tutors.keys())
            elif form.cleaned_data["rating"] == ">= 2 stars":
                high_rating_tutors = {
                    user: rating
                    for user, rating in tutor_ratings.items()
                    if rating >= 2
                }
                users = users.filter(id__in=high_rating_tutors.keys())
            elif form.cleaned_data["rating"] == ">= 3 stars":
                high_rating_tutors = {
                    user: rating
                    for user, rating in tutor_ratings.items()
                    if rating >= 3
                }
                users = users.filter(id__in=high_rating_tutors.keys())
            elif form.cleaned_data["rating"] == ">= 4 stars":
                high_rating_tutors = {
                    user: rating
                    for user, rating in tutor_ratings.items()
                    if rating >= 4
                }
                users = users.filter(id__in=high_rating_tutors.keys())
            elif form.cleaned_data["rating"] == "= 5 stars":
                high_rating_tutors = {
                    user: rating
                    for user, rating in tutor_ratings.items()
                    if rating >= 5
                }
                users = users.filter(id__in=high_rating_tutors.keys())
        if form.cleaned_data["category"]:
            category = form.cleaned_data["category"]
            if category != "..":
                users = users
                users_favorite_id = favorites.filter(category=category).values_list(
                    "tutor", flat=True
                )
                users = users.filter(user__in=users_favorite_id)
        if form.cleaned_data["sortBy"]:
            if form.cleaned_data["sortBy"] == "Highest Rating":
                users = list(users)
                users.sort(
                    key=lambda tutor: tutor_ratings.get(tutor.id, 0), reverse=True
                )
            elif form.cleaned_data["sortBy"] == "Highest Price":
                users = users.order_by("-salary_max")
            elif form.cleaned_data["sortBy"] == "Lowest Price":
                users = users.order_by("salary_max")
    categories = list(set(favorites.values_list("category", flat=True)))
    favorites = favorites.values_list("tutor", flat=True)

    return render(
        request,
        "TutorFilter/filter_results.html",
        {
            "form": form,
            "users": users,
            "average_ratings": tutor_ratings.items(),
            "favorites": favorites,
            "categories": categories,
            "MEDIA_URL": settings.MEDIA_URL,
        },
    )


def add_favorite(request):
    if request.method == "POST":
        category_name = request.POST.get("category_name")
        tutor_id = request.POST.get("tutor_id")
        # print(tutor_id)
        # print(category_name)
        tutor = ProfileT.objects.all().filter(user__id=tutor_id)[:1].get().user
        # Now, you can add this to your database
        new_record = Favorite(category=category_name, student=request.user, tutor=tutor)
        new_record.save()

        return JsonResponse(
            {"status": "success", "message": "Add the tutor successfully!"}
        )
    else:
        return JsonResponse({"status": "error", "message": "Invalid request"})


def remove_favorite(request):
    if request.method == "POST":

        tutor_id = request.POST.get("tutor_id")
        tutor = ProfileT.objects.all().filter(user__id=tutor_id)[:1].get().user
        Favorite.objects.filter(student=request.user, tutor=tutor).delete()

        return JsonResponse(
            {"status": "success", "message": "Remove the tutor successfully!"}
        )
    else:
        return JsonResponse({"status": "error", "message": "Invalid request"})


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

    reviews = (
        TutorReview.objects.all()
        .filter(tutor_id=user_id)
        .select_related("student_id__profiles")
    )

    average_rating = reviews.aggregate(Avg("rating"))["rating__avg"] or 0

    return render(
        request,
        "TutorFilter/view_tutor_profile.html",
        {
            "profilet": profilet,
            "expertise": expertises,
            "availability": availability,
            "reviews": reviews,
            "average_rating": average_rating,
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
    availabilities = Availability.objects.filter(user_id=tutor_id)

    if request.method == "POST":
        form = TutoringSessionRequestForm(
            request.POST, request.FILES, tutor_user=tutor_user
        )
        if form.is_valid():
            selected_timeslots = json.loads(
                request.POST.get("selected_timeslots", "[]")
            )
            for timeslot in selected_timeslots:
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
                    attachment=form.cleaned_data.get(
                        "attachment"
                    ),  # Include the attachment
                    status="Pending",
                )
                tutoring_session.save()

            return redirect("Dashboard:dashboard")
    else:
        form = TutoringSessionRequestForm(tutor_user=tutor_user)

    return render(
        request,
        "TutorFilter/request_tutoring_session.html",
        {"form": form, "tutor": tutor_profile, "availabilities": availabilities},
    )


def get_available_times(request, tutor_id, selected_date):
    if request.method == "POST":
        selected_date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
        day_of_week = selected_date_obj.strftime("%A")
        day = day_of_week
        availabilities = Availability.objects.filter(
            user_id=tutor_id, day_of_week=day.lower()
        )
        booked_sessions = TutoringSession.objects.filter(
            tutor_id=tutor_id, date=selected_date, status="Accepted"
        )
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
        return JsonResponse({"available_slots": available_slots, "day": day.lower()})
