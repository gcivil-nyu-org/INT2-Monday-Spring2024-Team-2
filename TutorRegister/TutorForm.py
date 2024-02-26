from django import forms
from django.core.validators import RegexValidator, MinValueValidator

class TutorForm(forms.Form):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    PREFERRED_MODE_CHOICES = [
        ('online', 'Online'),
        ('in_person', 'In-person'),
    ]

    gender = forms.ChoiceField(choices=GENDER_CHOICES, label='Gender')
    zip_code = forms.CharField(max_length=10, label='Zip Code', validators=[RegexValidator(r'^\d{5}$', message='Enter a valid ZIP code.')])
    major = forms.CharField(max_length=100, label='Major')
    preferred_mode = forms.ChoiceField(choices=PREFERRED_MODE_CHOICES, label='Preferred Mode')
    introduction = forms.CharField(widget=forms.Textarea, label='Introduction')
    min_salary = forms.IntegerField(validators=[MinValueValidator(0)], label='Minimum Salary ($)')
    max_salary = forms.IntegerField(validators=[MinValueValidator(0)], label='Maximum Salary ($)')

    def clean(self):
        cleaned_data = super().clean()
        min_salary = cleaned_data.get('min_salary')
        max_salary = cleaned_data.get('max_salary')

        if min_salary is not None and max_salary is not None and min_salary > max_salary:
            raise forms.ValidationError('Minimum salary must be less than or equal to maximum salary')