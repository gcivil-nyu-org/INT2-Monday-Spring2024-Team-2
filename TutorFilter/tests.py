from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from TutorRegister.models import (
    ProfileT,
    ProfileS,
    Expertise,
    UserType,
    Availability,
    TutoringSession,
)
from django.test import Client
from datetime import datetime, timedelta
from .forms import TutoringSessionRequestForm
import json



class TutorFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        # Create expertise, profile, and other necessary objects here
        cls.testuser = User.objects.create_user(
            username="testuser@example.com",
            password="testpassword",
        )
        cls.testuser2 = User.objects.create_user(
            username="testuser2@example.com",
            password="testpassword",
        )
        cls.testuser.usertype.user_type = "tutor"
        cls.testuser2.usertype.user_type = "student"
        cls.testuser.usertype.has_profile_complete = True
        cls.testuser2.usertype.has_profile_complete = True
        cls.testuser.usertype.save()
        cls.testuser2.usertype.save()
        Expertise.objects.create(user=cls.testuser, subject="math")
        ProfileT.objects.create(
            user=cls.testuser,
            preferred_mode="remote",
            grade="freshman",
            zip="12345",
            salary_min=50,
        )
        ProfileS.objects.create(
            user=cls.testuser2,
            school="CUNY",
            preferred_mode="remote",
            grade="undergrad",
            zip="12345",
        )
        # Assign the expertise to the user somehow, according to your model structure

    def test_filter_tutors(self):
        form_data = {
            "preferred_mode": "remote",
            "grade": "freshman",
            "expertise": "math",
            "zipcode": "12345",
            "salary_max": 60,
        }
        response = self.client.get(
            reverse("TutorFilter:filter_tutors"),
            form_data,
        )
        self.assertEqual(response.status_code, 200)
        users_in_context = response.context["users"]
        self.assertTrue(any(user.user == self.testuser for user in users_in_context))

    def test_filter_tutors2(self):
        c = Client()
        # Simulate a GET request with query parameters
        form_data2 = {
            "preferred_mode": "remote",
            "grade": "grad",
            "expertise": "math",
            "zipcode": "11111",
            "salary_max": 20,
        }
        # form = TutorFilterForm(data=form_data)

        response2 = c.post(reverse("TutorFilter:filter_tutors"), form_data2)

        # Check if the response is 200 OK
        self.assertEqual(response2.status_code, 200)

        response2 = c.get(
            reverse("TutorFilter:filter_tutors"),
            form_data2,
        )
        # Check if the response context contains the expected user
        self.assertEqual(len(response2.context["users"]), 0)

    def test_view_profile_tutor(self):
        # Test view_profile for a tutor user
        response = self.client.get(
            reverse("TutorFilter:view_profile", args=[self.testuser.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "TutorFilter/view_tutor_profile.html")

    def test_view_profile_student(self):
        # Test view_profile for a student user
        response = self.client.get(
            reverse("TutorFilter:view_profile", args=[self.testuser2.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "TutorFilter/view_student_profile.html")

    def test_view_tutor_profile(self):
        # Test view_tutor_profile
        response = self.client.get(
            reverse("TutorFilter:view_tutor_profile", args=[self.testuser.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "TutorFilter/view_tutor_profile.html")

    def test_view_student_profile(self):
        # Test view_student_profile
        response = self.client.get(
            reverse("TutorFilter:view_student_profile", args=[self.testuser2.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "TutorFilter/view_student_profile.html")


class TutoringSessionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="tutor@test.com", password="password123"
        )
        cls.user.usertype.user_type = "tutor"
        cls.user.usertype.save()
        cls.url = reverse("Dashboard:tutor_profile")
        ProfileT.objects.create(
            user=cls.user,
            fname="Test",
            lname="User",
            gender="prefernottosay",
            major="Computer Science",
            zip="00000",
            grade="grad",
            preferred_mode="remote",
            intro="ello \nyello \njelo",
        )
        Availability.objects.create(
            user=cls.user,
            day_of_week="monday",
            start_time=datetime.strptime("09:00", "%H:%M").time(),
            end_time=datetime.strptime("17:00", "%H:%M").time(),
        )
        Expertise.objects.create(user=cls.user, subject="math")
        User.objects.create_user(username="student", password="studentpassword")

    def setUp(self):
        self.client = Client()
        self.client.login(username="student", password="studentpassword")

    def test_request_tutoring_session_get(self):
        response = self.client.get(reverse("TutorFilter:request", args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], TutoringSessionRequestForm)

    def test_request_tutoring_session_post_valid(self):
        data = {
            "tutoring_mode": "remote",
            "subject": "math",
            "date": "2024-04-01",
            "offering_rate": 50,
            "message": "Looking forward to the session!",
            "selected_timeslots": json.dumps([{"start": "09:00", "end": "09:30"}]),
        }
        response = self.client.post(
            reverse("TutorFilter:request", args=[self.user.id]), data
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(TutoringSession.objects.exists())

    def test_request_tutoring_session_post_invalid(self):
        data = {
            "tutoring_mode": "",
            "subject": "Math",
            "date": "2024-03-25",
            "offering_rate": 50,
            "message": "Looking forward to the session!",
            "selected_timeslots": json.dumps([{"start": "09:00", "end": "09:30"}]),
        }
        response = self.client.post(
            reverse("TutorFilter:request", args=[self.user.id]), data
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(TutoringSession.objects.exists())

    def test_get_available_times(self):
        response = self.client.post(
            reverse(
                "TutorFilter:get-available-times", args=[self.user.id, "2024-04-01"]
            )
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn("available_slots", response_data)
        self.assertIn("day", response_data)
