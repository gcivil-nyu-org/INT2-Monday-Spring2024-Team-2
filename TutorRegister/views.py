from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import User

from .forms import RegisterUserForm


# register.html
def register(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Redirect to a success page or login page
            return HttpResponseRedirect(reverse('TutorRegister:success'))
        else:
            print("Invalid form")
    else:
        form = RegisterUserForm()
    return render(request, 'TutorRegister/register.html', {'form': form})


def success(request):
    return render(request, "TutorRegister/successful_register.html")