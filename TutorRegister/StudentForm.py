from django import forms
from django.core.validators import RegexValidator


class StudentForm(forms.Form):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
    ]

    PREFERRED_MODE_CHOICES = [
        ("online", "Online"),
        ("in_person", "In-person"),
    ]

    gender = forms.ChoiceField(choices=GENDER_CHOICES, label="Gender")
    zip_code = forms.CharField(
        max_length=10,
        label="Zip Code",
        validators=[RegexValidator(r"^\d{5}$", message="Enter a valid ZIP code.")],
    )
    school = forms.CharField(max_length=100, label="school")
    preferred_mode = forms.ChoiceField(
        choices=PREFERRED_MODE_CHOICES, label="Preferred Mode"
    )
    introduction = forms.CharField(widget=forms.Textarea, label="Introduction")

    def clean(self):
        return super().clean()
