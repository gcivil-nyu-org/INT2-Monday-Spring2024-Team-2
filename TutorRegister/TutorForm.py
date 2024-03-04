from django import forms
from django.core.validators import RegexValidator, MinValueValidator
from django.forms import ModelForm
from TutorRegister.models import ProfileT, Expertise


class TutorForm(ModelForm):
    GENDER_CHOICES = [
        ('female', 'Female'),
        ('male', 'Male'),
        ('prefernottosay','Prefer not to say'),
    ]

    MODE_CHOICES = [
        ('inperson', 'In-person'),
        ('remote', 'Remote'),
        ('both', 'Both'),
    ]
    
    DEGREE_CHOICES = [
        ('freshman', 'Freshman'),
        ('sophomore', 'Sophomore'),
        ('junior', 'Junior'),
        ('senior', 'Senior'),
        ('grad', 'Graduate Student'),
        ('phd', 'PhD Student'),
    ]   
    
    
    gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.Select(attrs={'class': 'form-select', 'style': 'margin-bottom: 10px;'}))
    preferred_mode = forms.ChoiceField(choices=MODE_CHOICES, widget=forms.Select(attrs={'class': 'form-select', 'style': 'margin-bottom: 10px;'}))
    grade = forms.ChoiceField(choices=DEGREE_CHOICES, widget=forms.Select(attrs={'class': 'form-select', 'style': 'margin-bottom: 10px;'}))

    # expertise = forms.ModelMultipleChoiceField(
    #     queryset=Expertise.objects.all(),
    #     widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
    # )

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
        }
        
        widgets = {
            'fname': forms.TextInput(attrs={'class': 'form-control', 'style': 'margin-bottom: 10px;'}),
            'lname': forms.TextInput(attrs={'class': 'form-control', 'style': 'margin-bottom: 10px;'}),
            'zip': forms.TextInput(attrs={'class': 'form-control', 'style': 'margin-bottom: 10px;'}),
            'major': forms.TextInput(attrs={'class': 'form-control', 'style': 'margin-bottom: 10px;'}),
            'salary_min': forms.TextInput(attrs={'class': 'form-control', 'style': 'margin-bottom: 10px;'}),
            'salary_max': forms.TextInput(attrs={'class': 'form-control', 'style': 'margin-bottom: 10px;'}),
            'intro': forms.Textarea(attrs={'class': 'form-control', 'style': 'margin-bottom: 10px;'}),

        }
        
    
    def clean(self):
        cleaned_data = super().clean()
        min_salary = cleaned_data.get("min_salary")
        max_salary = cleaned_data.get("max_salary")

        if (
            min_salary is not None
            and max_salary is not None
            and min_salary > max_salary
        ):
            raise forms.ValidationError(
                "Minimum salary must be less than or equal to maximum salary"
            )
