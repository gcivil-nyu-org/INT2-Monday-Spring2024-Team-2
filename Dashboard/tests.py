from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


# Create your tests here.
class StudentDashboardTestCase(TestCase):
    def setUp(self):
        # Create a user for testing login
        self.user = User.objects.create_user(username='test@example.com', password='12345')
        self.client = Client()
        
    def test_student_dashboard_view_with_login(self):
        self.client.login(username='test@example.com', password='12345')
        url = reverse("Dashboard:student_dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Dashboard/student_dashboard.html")
        
    def test_student_dashboard_view_without_login(self):
        url = reverse("Dashboard:student_dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        # Check if redirect to login page
        self.assertTrue(response.url.startswith('/auth/login/'))


class TutorDashboardTestCase(TestCase):
    def setUp(self):
        # Create a user for testing login
        self.user = User.objects.create_user(username='test@nyu.edu', password='12345')
        self.client = Client()
        
    def test_tutor_dashboard_view_with_login(self):
        self.client.login(username='test@nyu.edu', password='12345')
        url = reverse("Dashboard:tutor_dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Dashboard/tutor_dashboard.html")
        
    def test_tutor_dashboard_view_without_login(self):
        url = reverse("Dashboard:tutor_dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        # Check if redirect to login page
        self.assertTrue(response.url.startswith('/auth/login/'))


class HomepageTestCase(TestCase):
    def test_home_view(self):
        url = reverse("home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")
