from django import forms
from django.forms import ModelForm
from TutorRegister.models import ProfileT, Expertise, TutoringSession
from Dashboard.choices import EXPERTISE_CHOICES


class TutorFilterForm(forms.Form):
    # username = forms.CharField(required=False)
    # email = forms.EmailField(required=False)
    MODE_CHOICES = [
        ("..", ".."),
        ("inperson", "In-person"),
        ("remote", "Remote"),
        ("both", "Both"),
    ]

    GRADE_CHOICE = [
        ("..", ".."),
        ("freshman", "Freshman"),
        ("sophomore", "Sophomore"),
        ("junior", "Junior"),
        ("senior", "Senior"),
        ("grad", "Graduate Student"),
        ("phd", "PhD Student"),
    ]

    EXPERTISE_CHOICES = [
        ("..", ".."),
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

    preferred_mode = forms.ChoiceField(
        choices=MODE_CHOICES,
        widget=forms.Select(
            attrs={"class": "form-select", "style": "margin-bottom: 10px;"}
        ),
        required=False,
    )
    grade = forms.ChoiceField(
        choices=GRADE_CHOICE,
        widget=forms.Select(
            attrs={"class": "form-select", "style": "margin-bottom: 10px;"}
        ),
        required=False,
    )

    expertise = forms.ChoiceField(
        choices=EXPERTISE_CHOICES,
        widget=forms.Select(
            attrs={"class": "form-select", "style": "margin-bottom: 10px;"}
        ),
        required=False,
    )

    zipcode = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "form-control", "style": "margin-bottom: 10px;"}
        ),
        required=False,
    )
    salary_max = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={"class": "form-control", "style": "margin-bottom: 10px;"}
        ),
        required=False,
    )


class TutoringSessionRequestForm(forms.ModelForm):
    subject = forms.ChoiceField(choices=[])
    tutoring_mode = forms.ChoiceField(choices=[])

    def __init__(self, *args, tutor_user=None, **kwargs):
        super().__init__(*args, **kwargs)

        available_subject_choices = []
        if tutor_user:
            tutor_profile = ProfileT.objects.filter(user=tutor_user).first()
            expert_subjects = Expertise.objects.filter(user=tutor_user).values_list(
                "subject", flat=True
            )
            available_subject_choices = [
                choice for choice in EXPERTISE_CHOICES if choice[0] in expert_subjects
            ]

            self.fields["subject"].choices = available_subject_choices
            if tutor_profile:
                if tutor_profile.preferred_mode == "both":
                    mode_choices = [
                        ("inperson", "In Person"),
                        ("remote", "Remote"),
                        ("both", "Both"),
                    ]
                else:
                    mode_choices = [
                        (
                            tutor_profile.preferred_mode,
                            tutor_profile.preferred_mode.capitalize(),
                        )
                    ]

                self.fields["tutoring_mode"].choices = mode_choices

    class Meta:
        model = TutoringSession
        fields = ["tutoring_mode", "subject", "date", "offering_rate", "message"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "id": "date_selector"}),
            "offering_rate": forms.NumberInput(),
            "message": forms.Textarea(attrs={"rows": 3, "placeholder": "Message"}),
        }
