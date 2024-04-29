from django.forms import ModelForm
from django import forms
from TutorRegister.models import ProfileS
from django.core.exceptions import ValidationError
import re


class StudentForm(ModelForm):
    GENDER_CHOICES = [
        ("female", "Female"),
        ("male", "Male"),
        ("prefernottosay", "Prefer not to say"),
    ]

    GRADE_CHOICES = [
        ("1", "1st Grade"),
        ("2", "2nd Grade"),
        ("3", "3rd Grade"),
        ("4", "4th Grade"),
        ("5", "5th Grade"),
        ("6", "6th Grade"),
        ("7", "7th Grade"),
        ("8", "8th Grade"),
        ("9", "9th Grade"),
        ("10", "10th Grade"),
        ("11", "11th Grade"),
        ("12", "12th Grade"),
        ("undergrad", "Undergraduate"),
        ("grad", "Graduate"),
        ("postgrad", "Post-graduate"),
    ]

    MODE_CHOICES = [
        ("inperson", "In-person"),
        ("remote", "Remote"),
        ("both", "Both"),
    ]

    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.Select(
            attrs={"class": "form-select", "style": "margin-bottom: 10px;"}
        ),
    )
    zip = forms.CharField(required=True, max_length=5)
    grade = forms.ChoiceField(
        choices=GRADE_CHOICES,
        widget=forms.Select(
            attrs={"class": "form-select", "style": "margin-bottom: 10px;"}
        ),
    )
    preferred_mode = forms.ChoiceField(
        choices=MODE_CHOICES,
        widget=forms.Select(
            attrs={"class": "form-select", "style": "margin-bottom: 10px;"}
        ),
    )

    class Meta:
        model = ProfileS
        fields = [
            "fname",
            "lname",
            "gender",
            "zip",
            "school",
            "grade",
            "preferred_mode",
            "intro",
        ]
        labels = {
            "fname": "First Name",
            "lname": "Last Name",
            "gender": "Gender",
            "zip": "Zip Code",
            "school": "School",
            "grade": "Grade Level",
            "preferred_mode": "Preferred Tutoring Mode",
            "intro": "Introduction",
        }

        widgets = {
            "fname": forms.TextInput(
                attrs={"class": "form-control", "style": "margin-bottom: 10px;"}
            ),
            "lname": forms.TextInput(
                attrs={"class": "form-control", "style": "margin-bottom: 10px;"}
            ),
            "school": forms.TextInput(
                attrs={"class": "form-control", "style": "margin-bottom: 10px;"}
            ),
            "intro": forms.Textarea(
                attrs={"class": "form-control", "style": "margin-bottom: 10px;"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        zip = cleaned_data.get("zip")

        if bool(re.match(r"^\d{5}$", zip)) is False:
            raise ValidationError({"zip": "The zip code must be a 5-digit number."})

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.zip = self.cleaned_data["zip"]

        if commit:
            user.save()

        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({"class": "form-control"})


class StudentImageForm(forms.ModelForm):
    class Meta:
        model = ProfileS
        fields = ["image"]
        labels = {
            "image": "Profile Image",
        }
        widgets = {
            "image": forms.FileInput(
                attrs={"class": "form-control", "style": "margin-bottom: 10px;"}
            ),
        }
