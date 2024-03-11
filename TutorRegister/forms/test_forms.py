from django.test import TestCase
from django.contrib.auth.models import User
from TutorRegister.forms.register_login import RegisterUserForm

class RegisterUserFormTest(TestCase):
    def setUp(self):
        User.objects.create_user(
            username="existinguser@example.com", 
            email="existinguser@example.com", 
            password="12345"
        )

    def test_form_valid(self):
        form_data = {
            'user_type': 'student',
            'email': 'newuser@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password1': 'Password123...',
            'password2': 'Password123...'
        }
        form = RegisterUserForm(data=form_data)
        if not form.is_valid():
            print(form.errors)  # Print out the form errors for debugging
        self.assertTrue(form.is_valid())


    def test_form_invalid_email_exists(self):
        form_data = {
            'user_type': 'student',
            'email': 'existinguser@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password1': 'password123',
            'password2': 'password123'
        }
        form = RegisterUserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertEqual(form.errors['email'], ['A user with that email already exists.'])

    def test_form_invalid_tutor_email(self):
        form_data = {
            'user_type': 'tutor',
            'email': 'tutor@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password1': 'password123',
            'password2': 'password123'
        }
        form = RegisterUserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertEqual(form.errors['email'], ["Tutor email address must end with '@nyu.edu'."])

    def test_form_empty_first_name(self):
        form_data = {
            'user_type': 'student',
            'email': 'newuser@example.com',
            'first_name': '',
            'last_name': 'Doe',
            'password1': 'password123',
            'password2': 'password123'
        }
        form = RegisterUserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)
        self.assertEqual(form.errors['first_name'], ["This field is required.", "First name cannot be empty."])

    def test_form_empty_last_name(self):
        form_data = {
            'user_type': 'student',
            'email': 'newuser@example.com',
            'first_name': 'John',
            'last_name': '',
            'password1': 'password123',
            'password2': 'password123'
        }
        form = RegisterUserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('last_name', form.errors)
        self.assertEqual(form.errors['last_name'], ["This field is required.", "Last name cannot be empty."])
