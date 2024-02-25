from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class RegisterUserForm(UserCreationForm):
    USER_TYPES = (
        ('student', 'Student'),
        ('tutor', 'Tutor'),
    )

    user_type = forms.ChoiceField(choices=USER_TYPES, 
                                  required=True,
                                  widget=forms.RadioSelect)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, max_length=100)
    last_name = forms.CharField(required=True, max_length=100)

    class Meta:
        model = User
        fields = ['user_type', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        user_type = cleaned_data.get('user_type')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        
        if user_type == 'tutor' and not email.endswith('@nyu.edu'):
            raise ValidationError({'email': "Tutor email address must end with '@nyu.edu'."})
        
        if not first_name:
            raise ValidationError({'first_name': "First name cannot be empty."})
        
        if not last_name:
            raise ValidationError({'first_name': "First name cannot be empty."})
        
        
        return cleaned_data