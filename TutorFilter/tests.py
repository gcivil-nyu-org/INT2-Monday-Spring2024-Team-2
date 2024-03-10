from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from TutorRegister.models import ProfileT, Expertise
from django.test import Client


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

        response2 = c.post(
            reverse("TutorFilter:filter_tutors"),
            form_data2
        )

        # Check if the response is 200 OK
        self.assertEqual(response2.status_code, 200)

        response2 = c.get(
            reverse("TutorFilter:filter_tutors"),
            form_data2,
        )
        # Check if the response context contains the expected user
        users_in_context = response2.context["users"]
        # print(users_in_context)
        self.assertEqual(len(response2.context['users']), 0)
        
