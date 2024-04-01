from django.forms import ModelForm
from django import forms
from TutorRegister.models import TutorReview


class TutorReviewForm(forms.ModelForm):
    class Meta:
        model = TutorReview
        fields = ["rating", "review"]
