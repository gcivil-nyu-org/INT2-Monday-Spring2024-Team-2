from django import forms
from TutorRegister.models import Survey


class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ["q1", "q2", "q3"]
