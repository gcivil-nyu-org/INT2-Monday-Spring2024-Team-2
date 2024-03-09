from django.shortcuts import render
from .forms import TutorFilterForm
from TutorRegister.models import ProfileT, Availability, Expertise, UserType
from django.contrib.auth.models import User
from django.conf import settings


def filter_tutors(request):

    form = TutorFilterForm(request.GET)
    users_expertise = Expertise.objects.all()
    users = ProfileT.objects.all()
    # user_type = UserType.objects
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
