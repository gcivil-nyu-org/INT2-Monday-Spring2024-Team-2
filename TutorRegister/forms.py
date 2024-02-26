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
        email = cleaned_data.get('email').lower()
        user_type = cleaned_data.get('user_type')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        
        if User.objects.filter(username=email).exists():
            raise ValidationError({'email': "A user with that email already exists."})
        
        if user_type == 'tutor' and not email.endswith('@nyu.edu'):
            raise ValidationError({'email': "Tutor email address must end with '@nyu.edu'."})
        
        if not first_name:
            raise ValidationError({'first_name': "First name cannot be empty."})
        
        if not last_name:
            raise ValidationError({'first_name': "First name cannot be empty."})
        
        return cleaned_data
    
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']

        if commit:
            user.save()
            user.usertype.user_type = self.cleaned_data['user_type']
            user.usertype.save()
            
        return user
    
    def isTutor(self):
        return super().clean().get('user_type') == 'tutor'
    
    def isStudent(self):
        return super().clean().get('user_type') == 'student'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
            'class': 'form-control'
            })