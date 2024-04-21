from django import forms
from django.forms import ModelForm
from TutorRegister.models import ProfileT, Expertise, TutoringSession, Favorite
from Dashboard.choices import EXPERTISE_CHOICES
from django.utils import timezone
from datetime import timedelta
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError




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

    RATE_CHOICE = [
        ("..", ".."),
        (">= 1 star", ">= 1 star"),
        (">= 2 stars", ">= 2 stars"),
        (">= 3 stars", ">= 3 stars"),
        (">= 4 stars", ">= 4 stars"),
        ("= 5 stars", "= 5 stars"),
    ]

    SORT_CHOICE = [
        ("..", ".."),
        ("Highest Rating", "Highest Rating"),
        ("Highest Price", "Highest Price"),
        ("Lowest Price", "Lowest Price"),
    ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(TutorFilterForm, self).__init__(*args, **kwargs)
        # Set the choices for the 'category' field
        self.fields["category"] = forms.ChoiceField(
            choices=self.get_user_category_choices(user),
            required=False,
            widget=forms.Select(
                attrs={"class": "form-select border-2", "style": "margin-bottom: 10px;"}
            ),
            label="Select a category..",
        )

    preferred_mode = forms.ChoiceField(
        choices=MODE_CHOICES,
        widget=forms.Select(
            attrs={"class": "form-select border-2", "style": "margin-bottom: 10px;"}
        ),
        required=False,
    )
    grade = forms.ChoiceField(
        choices=GRADE_CHOICE,
        widget=forms.Select(
            attrs={"class": "form-select border-2", "style": "margin-bottom: 10px;"}
        ),
        required=False,
    )

    expertise = forms.ChoiceField(
        choices=EXPERTISE_CHOICES,
        widget=forms.Select(
            attrs={"class": "form-select border-2", "style": "margin-bottom: 10px;"}
        ),
        required=False,
    )

    zipcode = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "form-control border-2", "style": "margin-bottom: 10px;"}
        ),
        required=False,
    )
    salary_max = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={"class": "form-control border-2", "style": "margin-bottom: 10px;"}
        ),
        required=False,
    )
    rating = forms.ChoiceField(
        choices=RATE_CHOICE,
        widget=forms.Select(
            attrs={"class": "form-select border-2", "style": "margin-bottom: 10px;"}
        ),
        required=False,
    )
    saved = forms.ChoiceField(
        choices=SORT_CHOICE,
        widget=forms.Select(
            attrs={"class": "form-select border-2", "style": "margin-bottom: 10px;"}
        ),
        required=False,
    )
    sortBy = forms.ChoiceField(
        choices=SORT_CHOICE,
        widget=forms.Select(
            attrs={"class": "form-select border-2", "style": "margin-bottom: 10px;"}
        ),
        required=False,
    )

    def get_user_category_choices(self, user):
        if not user:
            return []

        # Here we filter the Favorite objects by the current user (student)
        # and create a tuple for the form's choices field
        res = []
        res = res + [
            (fav.category, fav.category)
            for fav in Favorite.objects.filter(student=user).distinct()
        ]
        res = list(set(res))
        res.insert(0, ("..", ".."))
        return res


class TutoringSessionRequestForm(forms.ModelForm):
    subject = forms.ChoiceField(
        choices=[], widget=forms.Select(attrs={"class": "form-select"})
    )
    tutoring_mode = forms.ChoiceField(
        choices=[], widget=forms.Select(attrs={"class": "form-select"})
    )
    
    offering_rate = forms.DecimalField(
        validators=[MinValueValidator(0.01)], 
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "0.01"})
    )

    date = forms.DateField(widget=forms.DateInput(attrs={
        "type": "date",
        "class": "form-control",
        "id": "date_selector"
    }))
    
    def __init__(self, *args, tutor_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['min'] = (timezone.localdate() + timedelta(days=1)).isoformat()
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
                        ),
                    ]

                self.fields["tutoring_mode"].choices = mode_choices
                
    def clean_date(self):
        date = self.cleaned_data['date']
        if date < timezone.localdate() + timedelta(days=1):
            raise ValidationError("Date cannot be in the past.")
        return date

    class Meta:
        model = TutoringSession
        fields = [
            "tutoring_mode",
            "subject",
            "date",
            "offering_rate",
            "message",
            "attachment",
        ]
        tomorrow = timezone.localdate() + timedelta(days=1)
        widgets = {
            # "date": forms.DateInput(
            #     attrs={
            #         "type": "date",
            #         "min": tomorrow.isoformat(),
            #         "class": "form-control",
            #         "id": "date_selector",
            #     }
            # ),
            # "offering_rate": forms.NumberInput(attrs={"class": "form-control"}),
            "message": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Message"}
            ),
            "attachment": forms.FileInput(attrs={"class": "form-control"}),
        }
