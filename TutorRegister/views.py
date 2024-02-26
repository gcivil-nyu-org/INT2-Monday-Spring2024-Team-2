from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import User

from .forms import RegisterUserForm
from .TutorForm import TutorForm
from .StudentForm import StudentForm
from verify_email.email_handler import send_verification_email

# register.html
def register(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            #user = form.save()
            inactive_user = send_verification_email(request, form)
            print(form.isTutor)
            # Redirect to a success page or login page
            if(form.isTutor()):
                return HttpResponseRedirect(reverse('TutorRegister:tutorinformation'))
            elif(form.isStudent()):
                return HttpResponseRedirect(reverse('TutorRegister:studentinformation'))
        else:
            print("Invalid form")
    else:
        form = RegisterUserForm()
    return render(request, 'TutorRegister/register.html', {'form': form})

def TutorInformation(request):
    if request.method == 'POST':
        form = TutorForm(request.POST)
        if form.is_valid():
            # Process the form data as needed
            # For example, save to the database
            # user = form.save()
            return render(request, "TutorRegister/successful_register.html")  # Redirect to a thank you page or another page
    else:
        form = TutorForm()
    return render(request, "TutorRegister/TutorInformation.html", {'form': form})

def StudentInformation(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            # Process the form data as needed
            # For example, save to the database
            # user = form.save()
            return render(request, "TutorRegister/successful_register.html")  # Redirect to a thank you page or another page
    else:
        form = StudentForm()
    return render(request, "TutorRegister/StudentInformation.html", {'form': form})

def success(request):
    return render(request, "TutorRegister/successful_register.html")

