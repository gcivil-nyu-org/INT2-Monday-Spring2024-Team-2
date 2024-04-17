from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField


class Expertise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    level = models.CharField(max_length=255)

    def human_readable_subject(self):
        return self.subject.replace("_", " ").capitalize()


# Two blank lines before the new class definition
class Availability(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=255)
    start_time = models.TimeField()
    end_time = models.TimeField()


# Two blank lines before the new class definition
class ProfileS(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fname = models.CharField(max_length=255)
    mname = models.CharField(max_length=255, blank=True)
    lname = models.CharField(max_length=255)
    gender = models.CharField(max_length=255)
    school = models.CharField(max_length=255)
    zip = models.CharField(max_length=255)
    grade = models.CharField(max_length=255)
    preferred_mode = models.CharField(max_length=255)
    intro = models.TextField()
    image = models.ImageField(upload_to="images/", default="images/profile_icon.png")


# Two blank lines before the new class definition
class ProfileT(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fname = models.CharField(max_length=255)
    mname = models.CharField(max_length=255, blank=True)
    lname = models.CharField(max_length=255)
    gender = models.CharField(max_length=255)
    major = models.CharField(max_length=255)
    zip = models.CharField(max_length=255)
    grade = models.CharField(max_length=255)
    preferred_mode = models.CharField(max_length=255)
    intro = models.TextField()
    salary_min = models.IntegerField(default=0)
    salary_max = models.IntegerField(default=0)
    image = models.ImageField(upload_to="images/", default="images/profile_icon.png")
    transcript = models.FileField(upload_to="transcripts/", null=True, blank=True)
    qualified = models.BooleanField(default=False, null=True, blank=True)


# Two blank lines before the new class definition
class UserType(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=100, null=True, blank=True)
    has_profile_complete = models.BooleanField(default=False, null=False)


class ChatSession(models.Model):
    tutor = models.ForeignKey(
        User, related_name="tutor_chats", on_delete=models.CASCADE
    )
    student = models.ForeignKey(
        User, related_name="student_chats", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    chat_session = models.ForeignKey(
        ChatSession, related_name="messages", on_delete=models.CASCADE
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class TutoringSession(models.Model):
    student_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="student_sessions"
    )
    tutor_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="tutor_sessions"
    )
    tutoring_mode = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField(default="12:00:00")
    end_time = models.TimeField(default="12:00:00")
    offering_rate = models.DecimalField(max_digits=6, decimal_places=0)
    message = models.TextField()
    status = models.TextField(default="Pending")
    attachment = models.FileField(upload_to="attachments/", null=True, blank=True)
    reviewed_by_student = models.BooleanField(default=False)
    meeting_link = models.CharField(max_length=100, null=True, blank=True)

    def human_readable_subject(self):
        return self.subject.replace("_", " ")


class TutorReview(models.Model):
    student_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="student_reviews"
    )
    tutor_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="tutor_reviews"
    )
    tutoring_session = models.ForeignKey(
        TutoringSession,
        on_delete=models.CASCADE,
        related_name="session_reviews",
        null=True,
    )
    review_date = models.DateField(auto_now_add=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    review = models.TextField()

    def __str__(self):
        return f"Review by {self.student_id} for {self.tutor_id}"


class Favorite(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="student_favorites"
    )
    tutor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="tutor_favorites"
    )
    category = models.CharField(max_length=100, null=True, blank=True)


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_post")
    title = models.CharField(max_length=250)
    content = models.TextField()
    label = models.CharField(max_length=100)
    post_date = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to="attachments/", null=True, blank=True)
    topics = models.CharField(models.CharField(), blank=True)

    def get_rating(self):
        upvotes = Vote.objects.filter(post=self, value=1).count()
        downvotes = Vote.objects.filter(post=self, value=-1).count()
        return upvotes - downvotes


class Reply(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_reply")
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="post_replies"
    )
    content = models.TextField()
    reply_date = models.DateTimeField(auto_now_add=True)


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_react")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_react")
    value = models.IntegerField(
        default=0
    )  # 1 for upvote, -1 for downvote, 0 for neutral

    class Meta:
        unique_together = ("user", "post")


class Survey(models.Model):
    session = models.ForeignKey(
        TutoringSession, on_delete=models.CASCADE, related_name="session_survey"
    )
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_reviewer"
    )
    reviewee = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_reviewee"
    )
    q1 = models.BooleanField(null=True, blank=True)
    q2 = models.BooleanField(null=True, blank=True)
    q3 = models.BooleanField(null=True, blank=True)
    completed = models.BooleanField(default=False, null=True, blank=True)


# Two blank lines before the new function definition
# Signal to automatically create or update UserType when a User instance is saved
@receiver(post_save, sender=User)
def create_or_update_user_type(sender, instance, created, **kwargs):
    if created:
        UserType.objects.create(user=instance)
    instance.usertype.save()
