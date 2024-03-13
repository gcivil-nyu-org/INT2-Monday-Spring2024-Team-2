from django.shortcuts import render,get_object_or_404
from .forms import TutorFilterForm
from TutorRegister.models import ProfileT, Availability, Expertise, UserType
from django.contrib.auth.models import User
from django.conf import settings


def filter_tutors(request):
    form = TutorFilterForm(request.GET)
    users_expertise = Expertise.objects.all()
    users = ProfileT.objects.all()
    has_profile = UserType.objects.all().filter(has_profile_complete = True).values_list("user", flat=True)
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

def view_tutor_profile(request, user_id):
    profilet = get_object_or_404(ProfileT, user=user_id)
    expertise = Expertise.objects.all().filter(user = profilet.user)#.filter(user=profilet.user)
    availability = Availability.objects.all().filter(user=profilet.user)
    return render(request, 'TutorFilter/view_tutor_profile.html', {'profilet': profilet,'expertise':expertise,'availability':availability,"MEDIA_URL": settings.MEDIA_URL,})
