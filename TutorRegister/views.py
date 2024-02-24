from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User

from .models import ProfileT, ProfileS
from .exceptions import EmailValidationError, PasswordValidationError, NameValidationError

import re


# TutorRegister.html
def register_tutor(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        firstName = request.post["firstName"]
        lastName = request.post["lastName"]
        
        try:
            if '@nyu.edu' not in email: 
                raise EmailValidationError
            if not (len(password) >= 6 and 
                    re.search("[a-z]", password) and 
                    re.search("[A-Z]", password) and
                    re.search("[0-9]", password)): 
                raise PasswordValidationError
            if not (len(firstName) > 0 and len(lastName) > 0):
                raise NameValidationError
            
            # Create the user
            user = User.objects.create(username=email, email=email, password=password, first_name=firstName, last_name=lastName)
            user.save()
            
            return redirect(reverse('tutor_info'), kwargs={'user_id': user.id})
            
        except Exception as e:
            error_message = "Failed to register. Please try again."
            if e is EmailValidationError: error_message = "Email must be a valid NYU email address."
            elif e is PasswordValidationError: error_message = "Password must be at least 6 characters long and contain at least one uppercase letter, one lowercase letter, and one number."
            elif e is NameValidationError: error_message = "Must enter a valid name."
            
            messages.error(request, error_message)
            return redirect('register_tutor')
             
    return render(request, "TutorRegister/TutorRegister.html")


def tutor_info(request, user_id):
    if request.method == "POST":
        firstName = request.POST["firstName"]
        lastName = request.POST["lastName"]
        gender = request.POST["gender"]
        major = request.POST["major"]
        zipCode = request.POST["zipCode"]
        
        try:
            tutor_profile = 
        
    return render(request, "TutorRegister/TutorInformation.html", {"user_id": user_id})


def register_student(request):
    return render(request, "TutorRegister/StudentParentsRegister.html")