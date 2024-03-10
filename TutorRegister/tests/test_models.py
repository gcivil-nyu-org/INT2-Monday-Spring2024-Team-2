from datetime import time

from django.test import TestCase
from django.contrib.auth.models import User
from TutorRegister.models import (
    Expertise,
    Availability,
    ProfileS,
    ProfileT,
    UserType,
    create_or_update_user_type,
)
from django.db.models.signals import post_save


class ExpertiseModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="test@example.com", password="12345"
        )
        Expertise.objects.create(user=cls.user, subject="math", level="advanced")

    def test_expertise_content(self):
        expertise = Expertise.objects.get(id=1)
        self.assertEqual(expertise.subject, "math")
        self.assertEqual(expertise.level, "advanced")


class AvailablilityModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="test@example.com", password="12345"
        )
        Availability.objects.create(
            user=cls.user,
            day_of_week="monday",
            start_time="10:00:00",
            end_time="13:00:00",
        )

    def test_availablility_content(self):
        availability = Availability.objects.get(id=1)
        self.assertEqual(availability.day_of_week, "monday")
        self.assertEqual(availability.start_time, time(10, 0))
        self.assertEqual(availability.end_time, time(13, 0))


class ProfileSModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="test@example.com", password="12345"
        )
        ProfileS.objects.create(
            user=cls.user,
            fname="Test",
            lname="User",
            gender="female",
            school="Test School",
            zip="00000",
            grade="1",
            preferred_mode="inperson",
            intro="hello \nhello \ngello",
        )

    def test_profiles_content(self):
        profiles = ProfileS.objects.get(id=1)
        self.assertEqual(profiles.fname, "Test")
        self.assertEqual(profiles.lname, "User")
        self.assertEqual(profiles.gender, "female")
        self.assertEqual(profiles.school, "Test School")
        self.assertEqual(profiles.zip, "00000")
        self.assertEqual(profiles.grade, "1")
        self.assertEqual(profiles.preferred_mode, "inperson")
        self.assertEqual(profiles.intro, "hello \nhello \ngello")


class ProfileTModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="test@nyu.edu", password="12345")
        ProfileT.objects.create(
            user=cls.user,
            fname="Test",
            lname="User",
            gender="prefernottosay",
            major="Computer Science",
            zip="00000",
            grade="graduate",
            preferred_mode="remote",
            intro="ello \nyello \njelo",
        )

    def test_profilet_content(self):
        profilet = ProfileT.objects.get(id=1)
        self.assertEqual(profilet.fname, "Test")
        self.assertEqual(profilet.lname, "User")
        self.assertEqual(profilet.gender, "prefernottosay")
        self.assertEqual(profilet.major, "Computer Science")
        self.assertEqual(profilet.zip, "00000")
        self.assertEqual(profilet.grade, "graduate")
        self.assertEqual(profilet.preferred_mode, "remote")
        self.assertEqual(profilet.intro, "ello \nyello \njelo")


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
