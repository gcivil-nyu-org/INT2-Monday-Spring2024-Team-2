from django.test import TestCase
from django.contrib.auth.models import User
from TutorRegister.forms.register_login import RegisterUserForm
from TutorRegister.forms.student_info import StudentForm
from TutorRegister.models import ProfileS


class RegisterUserFormTest(TestCase):
    def setUp(self):
        User.objects.create_user(
            username="existinguser@example.com",
            email="existinguser@example.com",
            password="12345",
        )

    def test_form_valid(self):
        form_data = {
            "user_type": "student",
            "email": "newuser@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password1": "Password123...",
            "password2": "Password123...",
        }
        form = RegisterUserForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_email_exists(self):
        form_data = {
            "user_type": "student",
            "email": "existinguser@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password1": "password123",
            "password2": "password123",
        }
        form = RegisterUserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertEqual(
            form.errors["email"], ["A user with that email already exists."]
        )

    def test_form_invalid_tutor_email(self):
        form_data = {
            "user_type": "tutor",
            "email": "tutor@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password1": "password123",
            "password2": "password123",
        }
        form = RegisterUserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertEqual(
            form.errors["email"], ["Tutor email address must end with '@nyu.edu'."]
        )

    def test_form_empty_first_name(self):
        form_data = {
            "user_type": "student",
            "email": "newuser@example.com",
            "first_name": "",
            "last_name": "Doe",
            "password1": "password123",
            "password2": "password123",
        }
        form = RegisterUserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)
        self.assertEqual(
            form.errors["first_name"],
            ["This field is required.", "First name cannot be empty."],
        )

    def test_form_empty_last_name(self):
        form_data = {
            "user_type": "student",
            "email": "newuser@example.com",
            "first_name": "John",
            "last_name": "",
            "password1": "password123",
            "password2": "password123",
        }
        form = RegisterUserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("last_name", form.errors)
        self.assertEqual(
            form.errors["last_name"],
            ["This field is required.", "Last name cannot be empty."],
        )

    def test_save_new_user(self):
        form_data = {
            "user_type": "student",
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password1": "Testpassword123",
            "password2": "Testpassword123",
        }
        form = RegisterUserForm(data=form_data)
        self.assertTrue(form.is_valid())

        user = form.save()
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, form_data["email"])
        self.assertEqual(user.first_name, form_data["first_name"])
        self.assertEqual(user.last_name, form_data["last_name"])
        self.assertTrue(user.check_password(form_data["password1"]))

    def test_save_existing_user(self):
        User.objects.create_user(
            username="existing@example.com", password="Testpassword123"
        )
        form_data = {
            "user_type": "student",
            "email": "existing@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password1": "Testpassword123",
            "password2": "Testpassword123",
        }
        form = RegisterUserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class StudentFormTestCase(TestCase):
    def test_student_form_valid_data(self):
        form = StudentForm(
            data={
                "fname": "John",
                "lname": "Doe",
                "gender": "male",
                "zip": "12345",
                "school": "ABC High School",
                "grade": "10",
                "preferred_mode": "inperson",
                "intro": "I am a 10th-grade student.",
            }
        )
        self.assertTrue(form.is_valid())

    def test_student_form_invalid_data(self):
        form = StudentForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 8)  # Assuming all fields are required

    def test_student_form_gender_choices(self):
        form = StudentForm()
        self.assertEqual(
            form.fields["gender"].choices,
            [
                ("female", "Female"),
                ("male", "Male"),
                ("prefernottosay", "Prefer not to say"),
            ],
        )

    def test_student_form_grade_choices(self):
        form = StudentForm()
        self.assertEqual(
            form.fields["grade"].choices,
            [
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
            ],
        )

    def test_student_form_preferred_mode_choices(self):
        form = StudentForm()
        self.assertEqual(
            form.fields["preferred_mode"].choices,
            [
                ("inperson", "In-person"),
                ("remote", "Remote"),
                ("both", "Both"),
            ],
        )

    def test_student_form_empty_fields(self):
        form = StudentForm(
            data={
                "fname": "",
                "lname": "",
                "gender": "",
                "zip": "",
                "school": "",
                "grade": "",
                "preferred_mode": "",
                "intro": "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 8)
