from typing import Any
from django.test.runner import DiscoverRunner
from django.core.cache import cache
from datetime import timedelta, date
from django.contrib.auth.models import User
from TutorRegister.models import (
    ProfileT,
    ProfileS,
    Expertise,
    Availability,
    TutoringSession,
    Favorite,
)


class GlobalTestRunner(DiscoverRunner):
    def setup_databases(self, **kwargs: Any) -> None:
        result = super().setup_databases(**kwargs)
        
        # Users
        self.tutor = User.objects.create_user(username="test@nyu.edu", password="testpassword", is_active=True)
        self.student = User.objects.create_user(username="test@example.com", password="testpassword", is_active=True)
        self.unverified_user = User.objects.create_user(username="unverified@example.com", password="testunverified", is_active=False)
        
        # UserTypes
        self.tutor.usertype.user_type = "tutor"
        self.tutor.usertype.save()
        self.student.usertype.user_type = "student"
        self.student.usertype.save()
        self.unverified_user.usertype.user_type = "student"
        self.unverified_user.usertype.save()
        
        # ProfileT
        self.profile_tutor = ProfileT.objects.create(user=self.tutor)
        
        # ProfieS
        self.profile_student = ProfileS.objects.create(user=self.student)
        
        # TutoringSession
        self.upcoming_session = TutoringSession.objects.create(
            student_id=self.student,
            tutor_id=self.tutor,
            date=date.today() + timedelta(days=5),
            start_time="10:00:00",
            end_time="11:00:00",
            status="Accepted",
            message="test",
            offering_rate=10,
            subject="test",
            tutoring_mode="remote",
        )
        self.past_session = TutoringSession.objects.create(
            student_id=self.student,
            tutor_id=self.tutor,
            date=date.today() - timedelta(days=5),
            start_time="10:00:00",
            end_time="11:00:00",
            status="Accepted",
            message="test",
            offering_rate=10,
            subject="test",
            tutoring_mode="remote",
        )
        self.pending_request = TutoringSession.objects.create(
            student_id=self.student,
            tutor_id=self.tutor,
            date=date.today() + timedelta(days=5),
            start_time="10:00:00",
            end_time="11:00:00",
            status="Pending",
            message="test",
            offering_rate=10,
            subject="test",
            tutoring_mode="remote",
        )
        
        cache.set_many({
            "tutor": self.tutor.id,
            "student": self.student.id,
            "unverified_user": self.unverified_user.id,
            "upcoming_session": self.upcoming_session.id,
            "past_session": self.past_session.id,
            "pending_request": self.pending_request.id
        })
        
        return result