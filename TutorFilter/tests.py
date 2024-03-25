from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from TutorRegister.models import (
    ProfileT,
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
    def setUpTestData(self):
        # Set up data for the whole TestCase
        # Create expertise, profile, and other necessary objects here
        self.testuser = User.objects.create_user(
            username="testuser@example.com",
            password="testpassword",
        )
        Expertise.objects.create(user=self.testuser, subject="math")
        ProfileT.objects.create(
            user=self.testuser,
            preferred_mode="remote",
            grade="freshman",
            zip="12345",
            salary_min=50,
        )
        UserType.objects.filter(user=self.testuser).update(has_profile_complete=True)
        # Assign the expertise to the user somehow, according to your model structure

    def test_filter_tutors(self):
        # Simulate a GET request with query parameters
        form_data = {
            "preferred_mode": "remote",
            "grade": "freshman",
            "expertise": "math",
            "zipcode": "12345",
            "salary_max": 60,
        }
        # form = TutorFilterForm(data=form_data)
        response = self.client.get(
            reverse("TutorFilter:filter_tutors"),
            form_data,
        )
        # Check if the response is 200 OK
        self.assertEqual(response.status_code, 200)
        # Check if the response context contains the expected user
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
