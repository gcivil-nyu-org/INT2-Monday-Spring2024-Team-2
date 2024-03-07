from django.shortcuts import render
from TutorRegister.models import ProfileS
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.template import loader


# @login_required
def Student_P_Display(request):
    student = ProfileS.objects.all().values()

    context = {
        "student_P": student,
    }

    return render(request, "Profile/studentProfile.html", context)
