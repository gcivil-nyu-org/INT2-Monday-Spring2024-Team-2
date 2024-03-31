from django.forms import ModelForm
from django import forms
from TutorRegister.models import TutorReview


class TutorReviewForm(forms.ModelForm):
    class Meta:
        model = TutorReview
        fields = ["rating", "review"]

    def __init__(self, *args, s_id=None, t_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.student_instance = s_id
        self.tutor_instance = t_id

        self.fields["review"].label = "Write your review"

    def clean_rating(self):
        rating = self.cleaned_data["rating"]
        return rating

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.student_id = self.student_instance
        instance.tutor_id = self.tutor_instance
        if commit:
            instance.save()
        return instance
