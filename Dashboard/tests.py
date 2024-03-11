from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from .views import StudentInformation
from TutorRegister.models import ProfileS
from .forms.student_info import StudentForm


# Create your tests here.
class StudentDashboardTestCase(TestCase):
    def setUp(self):
        # Create a user for testing login
        self.user = User.objects.create_user(
            username="test@example.com", password="12345"
        )
        self.client = Client()

    def test_student_dashboard_view_with_login(self):
        self.client.login(username="test@example.com", password="12345")
        url = reverse("Dashboard:student_dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Dashboard/student_dashboard.html")

    def test_student_dashboard_view_without_login(self):
        url = reverse("Dashboard:student_dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        # Check if redirect to login page
        self.assertTrue(response.url.startswith("/auth/login/"))


class TutorDashboardTestCase(TestCase):
    def setUp(self):
        # Create a user for testing login
        self.user = User.objects.create_user(username="test@nyu.edu", password="12345")
        self.client = Client()

    def test_tutor_dashboard_view_with_login(self):
        self.client.login(username="test@nyu.edu", password="12345")
        url = reverse("Dashboard:tutor_dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Dashboard/tutor_dashboard.html")

    def test_tutor_dashboard_view_without_login(self):
        url = reverse("Dashboard:tutor_dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        # Check if redirect to login page
        self.assertTrue(response.url.startswith("/auth/login/"))


class HomepageTestCase(TestCase):
    def test_home_view(self):
        url = reverse("home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")


class StudentInformationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@example.com", password="12345"
        )
        self.client = Client(username="test@example.com", password="12345")
        self.factory = RequestFactory()

    def test_student_information_view(self):
        url = reverse("Dashboard:student_profile")
        profile, created = ProfileS.objects.get_or_create(user=self.user)

        form_data = {
            "fname": "Test",
            "lname": "User",
            "gender": "female",
            "zip": "12345",
            "school": "Test School",
            "grade": "1",
            "preferred_mode": "remote",
            "intro": "Hello, this is a test.",
        }

        student_form = StudentForm(data=form_data, instance=profile)
        request = self.factory.post(url, data=student_form.data)
        request.user = self.user
        response = StudentInformation(request)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.user.usertype.has_profile_complete)

    def tearDown(self):
        self.user.delete()


class LogoutTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@example.com", password="12345"
        )
        self.client = Client(username="test@example.com", password="12345")

    def test_logout_view(self):
        self.assertNotEqual(str(self.user), "AnonymousUser")
        response = self.client.get(reverse("Dashboard:logout"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))

        user_after_logout = response.wsgi_request.user
        self.assertEqual(str(user_after_logout), "AnonymousUser")

    def tearDown(self):
        self.user.delete()
