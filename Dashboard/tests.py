from django.test import (
    TestCase,
    Client,
    RequestFactory,
    override_settings,
    TransactionTestCase,
)
from django.urls import reverse
from django.contrib.auth.models import User
from TutorRegister.models import (
    Expertise,
    Availability,
    ProfileT,
    TutoringSession,
    TutorReview,
)
from TutorNYU.form import ContactForm
import json
from .views import (
    StudentInformation,
    Requests,
    TutorFeedback,
    AdminDashboard,
    download_attachment,
    Survey,
)
from TutorNYU.views import contact
from TutorRegister.models import ProfileS
from .templatetags.custom_filters import remove_prefix
from .forms.student_info import StudentForm
from .forms.tutor_info import TutorForm
from .forms.survey_form import SurveyForm
from django.core import mail
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from datetime import datetime, time
import mimetypes


# Create your tests here.
class StudentDashboardTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_student_dashboard_view_with_login(self):
        self.client.login(username="test@example.com", password="testpassword")
        url = reverse("Dashboard:dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Dashboard/dashboard.html")

    def test_student_dashboard_view_without_login(self):
        url = reverse("Dashboard:dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        # Check if redirect to login page
        self.assertTrue(response.url.startswith("/auth/login/"))


class TutorDashboardTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_tutor_dashboard_view_with_login(self):
        self.client.login(username="test@nyu.edu", password="testpassword")
        url = reverse("Dashboard:dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Dashboard/dashboard.html")

    def test_tutor_dashboard_view_without_login(self):
        url = reverse("Dashboard:dashboard")
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


class ContactTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_contact_post(self):
        url = reverse("contact_us")
        form_data = {
            "full_name": "John Doe",
            "email": "john@example.com",
            "phone": "1234567890",
            "message": "Test message",
        }
        form = ContactForm(data=form_data)
        print("Valid:", form.is_valid())
        print("Errors:", form.errors)
        request = self.factory.post(url, data=form.data)
        response = contact(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)


class TutorInformationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.get(pk=cache.get("tutor"))
        cls.url = reverse("Dashboard:tutor_profile")

    def setUp(self):
        self.client = Client()
        self.client.login(username="test@nyu.edu", password="testpassword")

    def test_get_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("tutor_form", response.context)
        self.assertIn("availability_form", response.context)
        self.assertIn("initial_availabilities_json", response.context)
        self.assertTemplateUsed(response, "Dashboard/tutor_info.html")

    def test_post_request(self):
        test_file_path = os.path.join(
            os.path.dirname(__file__), "test_files", "random.pdf"
        )
        with open(test_file_path, "rb") as f:
            transcript_file = SimpleUploadedFile(
                "random.pdf", f.read(), content_type="application/pdf"
            )

        post_data = {
            "fname": "Test",
            "lname": "User",
            "gender": "male",
            "zip": "00000",
            "grade": "grad",
            "major": "Computer Science",
            "preferred_mode": "remote",
            "salary_min": 20,
            "salary_max": 50,
            "intro": "This is a test introduction.",
            "expertise": ["math", "computer_sci"],
            "day_of_week": "monday",
            "start_time": "10:00",
            "end_time": "12:00",
            "availabilities": json.dumps(
                [
                    {
                        "day_of_week": "monday",
                        "start_time": "10:00",
                        "end_time": "12:00",
                    },
                    {
                        "day_of_week": "wednesday",
                        "start_time": "14:00",
                        "end_time": "16:00",
                    },
                ]
            ),
        }

        # Include the transcript file in the request.FILES dictionary
        response = self.client.post(
            self.url, {**post_data, "transcript": transcript_file}, follow=True
        )

        self.assertRedirects(
            response,
            reverse("Dashboard:dashboard"),
            status_code=302,
            target_status_code=200,
        )

        self.assertTrue(ProfileT.objects.filter(user=self.user).exists())
        self.assertEqual(
            Expertise.objects.filter(user=self.user).count(),
            len(post_data["expertise"]),
        )
        self.assertTrue(Availability.objects.filter(user=self.user).exists())


class StudentInformationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.get(pk=cache.get("student"))
        self.client = Client(username="test@example.com", password="testpassword")
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


class CancelSessionTestCase(TestCase):
    def setUp(self):
        self.session = TutoringSession.objects.get(pk=cache.get("upcoming_session"))

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_cancel_session(self):
        self.client.login(username="test@nyu.edu", password="testpassword")
        response = self.client.get(
            reverse("Dashboard:cancel_session", args=(self.session.pk,))
        )
        self.assertEqual(response.status_code, 302)
        self.session.refresh_from_db()
        self.assertEqual(self.session.status, "Cancelled")
        self.assertEqual(len(mail.outbox), 1)

    def tearDown(self) -> None:
        self.session.status = "Accepted"
        self.session.save()
        super().tearDown()


class RequestsTestCase(TestCase):
    def setUp(self):
        self.tutor = User.objects.get(pk=cache.get("tutor"))

    def test_tutor_request(self):
        request = RequestFactory().get(reverse("Dashboard:requests"))
        request.user = self.tutor
        response = Requests(request)
        self.assertEqual(response.status_code, 200)


class AcceptRequestTestCase(TestCase):
    def setUp(self):
        self.session = TutoringSession.objects.get(pk=cache.get("pending_request"))
        self.client = Client()

    def test_accept_request(self):
        self.client.login(username="test@nyu.edu", password="testpassword")
        response = self.client.get(
            reverse("Dashboard:accept_request", args=(self.session.pk,))
        )
        self.assertEqual(response.status_code, 302)
        self.session.refresh_from_db()
        self.assertEqual(self.session.status, "Accepted")

    def tearDown(self) -> None:
        self.session.status = "Pending"
        self.session.save()
        super().tearDown()


class DeclineRequestTestCase(TestCase):
    def setUp(self):
        self.session = TutoringSession.objects.get(pk=cache.get("pending_request"))
        self.client = Client()

    def test_decline_request(self):
        self.client.login(username="test@nyu.edu", password="testpassword")
        response = self.client.get(
            reverse("Dashboard:decline_request", args=(self.session.pk,))
        )
        self.assertEqual(response.status_code, 302)
        self.session.refresh_from_db()
        self.assertEqual(self.session.status, "Declined")

    def tearDown(self) -> None:
        self.session.status = "Pending"
        self.session.save()
        super().tearDown()


class LogoutTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.get(pk=cache.get("student"))
        self.client = Client()
        self.client.login(username="test@example.com", password="testpassword")

    def test_logout_view(self):
        self.assertNotEqual(str(self.user), "AnonymousUser")
        response = self.client.get(reverse("Dashboard:logout"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))

        user_after_logout = response.wsgi_request.user
        self.assertEqual(str(user_after_logout), "AnonymousUser")


class ProvideFeedbackTestCase(TestCase):
    def setUp(self):
        self.session = TutoringSession.objects.get(pk=cache.get("past_session"))
        self.client = Client()
        self.client.login(username="test@example.com", password="testpassword")

    def test_provide_feedback(self):
        response = self.client.post(
            reverse("Dashboard:feedback", args=[self.session.pk]),
            {"rating": 5.0, "review": "Great tutor!"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            TutoringSession.objects.get(pk=self.session.pk).reviewed_by_student
        )


class SurveyTestCase(TestCase):
    def setUp(self):
        self.session = TutoringSession.objects.get(pk=cache.get("past_session"))
        self.client = Client()
        self.client.login(username="test@example.com", password="testpassword")

    def test_submit_survey(self):
        response = self.client.post(
            reverse("Dashboard:survey", args=[self.session.pk]),
            {"q1": "True", "q2": "True", "q3": "True"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            TutoringSession.objects.get(pk=self.session.pk).survey_completed
        )


class TutorFeedbackTestCase(TestCase):
    def setUp(self):
        self.tutor = User.objects.get(pk=cache.get("tutor"))
        self.student = User.objects.get(pk=cache.get("student"))
        self.session = TutoringSession.objects.get(pk=cache.get("past_session"))
        self.review = TutorReview.objects.create(
            tutor_id=self.tutor,
            student_id=self.student,
            tutoring_session=self.session,
            rating=4.5,
            review="Good tutor",
        )
        self.factory = RequestFactory()

    def test_tutor_feedback(self):
        self.client.force_login(self.tutor)
        request = self.factory.get(reverse("Dashboard:tutor_feedback"))
        request.user = self.tutor
        response = TutorFeedback(request)
        self.assertEqual(response.status_code, 200)


class AdminDashboardTestCase(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin", password="admin"
        )
        self.client = Client()
        self.tutor = User.objects.get(pk=cache.get("tutor"))
        Expertise.objects.create(subject="Math", user=self.tutor)

    def test_admin_dashboard(self):
        self.client.login(username="admin", password="admin")
        response = self.client.get(reverse("Dashboard:admin_dashboard"))
        self.assertEqual(response.status_code, 200)


class VideoCallTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_video_call_tutor(self):
        self.client.login(username="test@nyu.edu", password="testpassword")
        response = self.client.get(reverse("Dashboard:video_call"))
        self.assertEqual(response.status_code, 200)

    def test_video_call_student(self):
        self.client.login(username="test@example.com", password="testpassword")
        response = self.client.get(reverse("Dashboard:video_call"))
        self.assertEqual(response.status_code, 200)


class UpdateQualificationTestCase(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin", password="admin"
        )
        self.client = Client()
        self.tutor = User.objects.get(pk=cache.get("tutor"))
        self.tutor_profile = ProfileT.objects.get(user=self.tutor)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_update_qualifiction_qualified(self):
        self.tutor_profile.qualified = True
        self.client.login(username="admin", password="admin")
        response = self.client.post(
            reverse("Dashboard:update_qualification"),
            {"tutor_id": self.tutor_profile.id, "qualification": "qualified"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_update_qualifiction_unqualified(self):
        self.tutor_profile.qualified = False
        self.client.login(username="admin", password="admin")
        response = self.client.post(
            reverse("Dashboard:update_qualification"),
            {"tutor_id": self.tutor_profile.id, "qualification": "unqualified"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)


class RemovePrefixTestCase(TestCase):
    def test_remove_prefix_starts_with_prefix(self):
        value = "foobar"
        prefix = "foo"
        expected_result = "bar"
        self.assertEqual(remove_prefix(value, prefix), expected_result)

    def test_remove_prefix_without_prefix(self):
        value = "foo"
        prefix = "baz"
        expected_result = "foo"
        self.assertEqual(remove_prefix(value, prefix), expected_result)


class DownloadAttachmentTestCase(TestCase):
    def setUp(self):
        # Set up a user and log in
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client = Client()
        self.client.login(username="testuser", password="12345")

        # Ensure to include all required fields for the TutoringSession
        self.attachment = SimpleUploadedFile(
            "attachment.txt",
            b"Dummy file content of the attachment.",
            content_type="text/plain",
        )
        self.session = TutoringSession.objects.create(
            attachment=self.attachment,
            date=datetime.now().date(),
            offering_rate=55,
            student_id_id=1,
            tutor_id_id=10,
            start_time=time(12, 0),
            end_time=time(14, 0),
            status="Pending",
        )
        self.session.save()

    def test_download_attachment(self):
        # Build the URL and make the request
        url = reverse(
            "Dashboard:download_attachment", kwargs={"session_id": self.session.pk}
        )
        response = self.client.get(url)

        # Check response status code
        self.assertEqual(response.status_code, 200)

        # Check the content-type header
        self.assertEqual(response["Content-Type"], "text/plain")

        # Check the content-disposition header for correct filename
        self.assertIn(
            f'attachment; filename="{self.attachment.name}"',
            response["Content-Disposition"],
        )

        # Gather the streamed content and assert its content
        content = b"".join(response.streaming_content)
        self.assertEqual(content, b"Dummy file content of the attachment.")

    def tearDown(self):
        # Clean up after each test
        self.user.delete()
        self.session.delete()


class DownloadTranscriptTestCase(TestCase):
    def setUp(self):
        # Set up a user and log in
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client = Client()
        self.client.login(username="testuser", password="12345")

        # Set up a ProfileT with a transcript
        self.transcript = SimpleUploadedFile(
            "transcript.pdf",
            b"PDF file content for testing",
            content_type="application/pdf",
        )
        self.tutor_profile = ProfileT.objects.create(
            user=self.user,
            transcript=self.transcript,
        )

    def test_download_transcript(self):
        # Build the URL and make the request
        url = reverse(
            "Dashboard:download_transcript", kwargs={"tutor_id": self.tutor_profile.pk}
        )
        response = self.client.get(url)

        # Check response status code
        self.assertEqual(response.status_code, 200)

        # Check the content-type header
        content_type, _ = mimetypes.guess_type(self.transcript.name)
        self.assertEqual(response["Content-Type"], content_type)

        # Check the content-disposition header for correct filename
        self.assertIn(
            f'attachment; filename="{self.transcript.name}"',
            response["Content-Disposition"],
        )

        # Gather the streamed content and assert its content
        content = b"".join(response.streaming_content)
        self.assertEqual(content, b"PDF file content for testing")

    def tearDown(self):
        # Clean up after each test
        self.user.delete()
        self.tutor_profile.delete()
