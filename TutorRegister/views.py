from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

from .forms import RegisterUserForm
from .TutorForm import TutorForm, AvailabilityForm
from .StudentForm import StudentForm
from .models import Expertise, Availability

from verify_email.email_handler import send_verification_email


# register.html
def register(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            #user = form.save()
            form.save()
            #inactive_user = send_verification_email(request, form)
            send_verification_email(request, form)
            print(form.isTutor)
            # Redirect to a success page or login page
            if form.isTutor():
                return HttpResponseRedirect(reverse("TutorRegister:tutorinformation"))
            elif form.isStudent():
                return HttpResponseRedirect(reverse("TutorRegister:studentinformation"))
        else:
            print("Invalid form")
    else:
        form = RegisterUserForm()
    return render(request, "TutorRegister/register.html", {"form": form})


def TutorInformation(request):
    if request.method == 'POST':
        tutor_form = TutorForm(request.POST)
        availability_form = AvailabilityForm(request.POST)
        if tutor_form.is_valid() and availability_form.is_valid():
            # save tutor profile data
            user = request.user
            profile = tutor_form.save(commit=False)
            profile.user = user
            profile.save()
            
            # save availability data
            availability_data = availability_form.cleaned_data
            availability_data['user'] = user
            Availability.objects.create(**availability_data)
            
            # save expertise data to database
            selected_expertise = request.POST.getlist('expertise')
            if selected_expertise:
                for expertise in selected_expertise:
                    Expertise.objects.create(user=user, subject=expertise)
            return redirect('TutorRegister/successful_register.html')
    else:
        tutor_form = TutorForm()
        availability_form = AvailabilityForm()
    context = {
        'tutor_form': tutor_form,
        'availability_form': availability_form,}
    return render(request, "TutorRegister/TutorInformation.html", context)


def StudentInformation(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            user = request.user
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect('TutorRegister/successful_register.html')
    else:
        form = StudentForm()
    context = {'form': form}
    return render(request, "TutorRegister/StudentInformation.html", context)


def success(request):
    return render(request, "TutorRegister/successful_register.html")


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # print(user.usertype.user_type)
                if user.usertype.user_type == "tutor":
                    return render(request, "TutorRegister/tutor_dashboard.html")
                elif user.usertype.user_type == "student":
                    return render(request, "TutorRegister/student_dashboard.html")
                return render(request, "TutorRegister/successful_register.html")
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid email or password.")
    form = AuthenticationForm()
    return render(request, "TutorRegister/login.html", {"login_form": form})
