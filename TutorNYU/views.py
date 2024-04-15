from django.shortcuts import render
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.urls import reverse
from .form import ContactForm


# Create your views here.
def home(request):
    return render(request, "home.html")


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data.get("full_name")
            email = form.cleaned_data.get("email")
            phone = form.cleaned_data.get("phone")
            message = form.cleaned_data.get("message")

            subject = f"[Inquiry] From {full_name}"
            phone_display = phone if phone else "Not Available"
            body = (
                f"""You have received a new inquiry:\n\nFull Name: {full_name}\n"""
                f"""Email: {email}\nPhone: {phone_display}\nMessage:\n{message}"""
            )
            sender_email = "tutornyuengineeringverify@gmail.com"
            recipient_email = "vickyhuang9311@gmail.com"

            send_mail(subject, body, sender_email, [recipient_email])
            form = ContactForm()
            return render(request, "contact_us.html", {"form": form, "success": True})

    else:
        form = ContactForm()
    return render(request, "contact_us.html", {"form": form, "success": False})
