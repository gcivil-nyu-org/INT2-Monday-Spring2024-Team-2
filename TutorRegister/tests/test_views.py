from django.test import TestCase
from django.urls import reverse


class RegisterTestCase(TestCase):
    def test_register_view(self):
        url = reverse("TutorRegister:register")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "TutorRegister/register.html")
        
        
class SuccessTestCase(TestCase):
    def test_success_view(self):
        url = reverse("TutorRegister:success")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "TutorRegister/successful_register.html")
        
        
class LoginTestCase(TestCase):
    def test_login_view(self):
        url = reverse("TutorRegister:login")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "TutorRegister/login.html")