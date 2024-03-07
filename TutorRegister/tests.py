# Create your tests here.
from django.test import TestCase
from django.contrib.auth.models import User
from .models import UserType
from .models import create_or_update_user_type
from django.db.models.signals import post_save


class UserTypeSignalTest(TestCase):
    def setUp(self):
        post_save.connect(create_or_update_user_type, sender=User)

        # Create a test user
        self.user = User.objects.create_user(
            username="testuser@example.com",
            password="testpassword",
        )

    def test_create_or_update_user_type_signal(self):
        user = User.objects.get(username="testuser@example.com")

        # Check if the UserType instance is created or updated
        self.assertTrue(UserType.objects.filter(user=user).exists())

    def tearDown(self):
        post_save.disconnect(create_or_update_user_type, sender=User)
