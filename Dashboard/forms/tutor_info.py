from django import forms

# from django.core.validators import RegexValidator, MinValueValidator
from django.forms import ModelForm
from TutorRegister.models import ProfileT, Availability


class TutorForm(ModelForm):
    GENDER_CHOICES = [
        ("female", "Female"),
        ("male", "Male"),
        ("prefernottosay", "Prefer not to say"),
    ]

    MODE_CHOICES = [
        ("inperson", "In-person"),
        ("remote", "Remote"),
        ("both", "Both"),
    ]

    GRADE_CHOICE = [
        ("freshman", "Freshman"),
        ("sophomore", "Sophomore"),
        ("junior", "Junior"),
        ("senior", "Senior"),
        ("grad", "Graduate Student"),
        ("phd", "PhD Student"),
    ]

    EXPERTISE_CHOICES = [
        ("math", "Mathematics"),
        ("algebra", "Algebra"),
        ("calculus", "Calculus"),
        ("computer_sci", "Computer Science"),
        ("elementary_math", "Elementary Math"),
        ("geometry", "Geometry"),
        ("high_school_math", "High School Math"),
        ("regents_math", "Regents Math"),
        ("act", "ACT"),
        ("gmat", "GMAT"),
        ("gre", "GRE"),
        ("ielts", "IELTS"),
        ("lsat", "LSAT"),
        ("sat", "SAT"),
        ("toefl", "TOEFL"),
        ("esl", "ESL"),
        ("economics", "Economics"),
        ("elementry_reading", "Elementary Reading"),
        ("history", "History"),
        ("english", "English"),
        ("social_studies", "Social Studies"),
        ("writing", "Writing"),
        ("biology", "Biology"),
        ("physics", "Physics"),
        ("arabic", "Arabic"),
        ("chinese", "Chinese"),
        ("french", "French"),
        ("italian", "Italian"),
        ("german", "German"),
        ("russian", "Russian"),
        ("spanish", "Spanish"),
        ("cello", "Cello"),
        ("piano", "Piano"),
        ("singing", "Singing"),
        ("violin", "Violin"),
    ]

    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
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
    grade = forms.ChoiceField(
        choices=GRADE_CHOICE,
        widget=forms.Select(
            attrs={"class": "form-select", "style": "margin-bottom: 10px;"}
        ),
    )

    expertise = forms.MultipleChoiceField(
        choices=EXPERTISE_CHOICES,
        widget=forms.SelectMultiple(
            attrs={"class": "form-select", "style": "margin-bottom: 10px;"}
        ),
        required=False,
    )

    class Meta:
        model = ProfileT
        fields = [
            "fname",
            "lname",
            "gender",
            "zip",
            "grade",
            "major",
            "preferred_mode",
            "salary_min",
            "salary_max",
            "intro",
            "image",
        ]
        labels = {
            "fname": "First Name",
            "lname": "Last Name",
            "gender": "Gender",
            "zip": "Zip Code",
            "grade": "Grade",
            "major": "Major",
            "preferred_mode": "Preferred Tutoring Mode",
            "intro": "Introduction",
            "salary_min": "Minimum Hourly Rate",
            "salary_max": "Maximum Hourly Rate",
            "image": "Profile Image",
        }

        widgets = {
            "fname": forms.TextInput(
                attrs={"class": "form-control", "style": "margin-bottom: 10px;"}
            ),
            "lname": forms.TextInput(
                attrs={"class": "form-control", "style": "margin-bottom: 10px;"}
            ),
            "zip": forms.TextInput(
                attrs={"class": "form-control", "style": "margin-bottom: 10px;"}
            ),
            "major": forms.TextInput(
                attrs={"class": "form-control", "style": "margin-bottom: 10px;"}
            ),
            "salary_min": forms.NumberInput(
                attrs={"class": "form-control", "style": "margin-bottom: 10px; col: sm"}
            ),
            "salary_max": forms.NumberInput(
                attrs={"class": "form-control", "style": "margin-bottom: 10px;"}
            ),
            "intro": forms.Textarea(
                attrs={"class": "form-control", "style": "margin-bottom: 10px;"}
            ),
            "image": forms.FileInput(  # Widget for the image field
                attrs={"class": "form-control", "style": "margin-bottom: 10px;"}
            ),
        }


class AvailabilityForm(forms.ModelForm):
    DAY_CHOICES = [
        ("monday", "Monday"),
        ("tuesday", "Tuesday"),
        ("wednesday", "Wednesday"),
        ("thursday", "Thursday"),
        ("friday", "Friday"),
        ("saturday", "Saturday"),
        ("sunday", "Sunday"),
    ]

    day_of_week = forms.ChoiceField(
        choices=DAY_CHOICES,
        widget=forms.Select(
            attrs={"class": "form-select", "style": "margin-bottom: 10px;"}
        ),
    )

    class Meta:
        model = Availability
        fields = [
            "day_of_week",
            "start_time",
            "end_time",
        ]

        widgets = {
            "start_time": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                    "style": "margin-bottom: 10px;",
                }
            ),
            "end_time": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                    "style": "margin-bottom: 10px;",
                }
            ),
        }
