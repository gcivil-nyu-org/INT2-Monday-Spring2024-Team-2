from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Expertise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    level = models.CharField(max_length=255)


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


# Two blank lines before the new class definition
class UserType(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=100, null=True, blank=True)
    has_profile_complete = models.BooleanField(default=False, null=False)


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
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True)
    
    def human_readable_subject(self):
        return self.subject.replace("_", " ")

class TutorReview(models.Model):
    student_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="student_reviews"
    )
    tutor_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="tutor_reviews"
    )
    review_date = models.DateField(auto_now_add=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    review = models.TextField()

    def __str__(self):
        return f"Review by {self.student_id} for {self.tutor_id}"



# Two blank lines before the new function definition
# Signal to automatically create or update UserType when a User instance is saved
@receiver(post_save, sender=User)
def create_or_update_user_type(sender, instance, created, **kwargs):
    if created:
        UserType.objects.create(user=instance)
    instance.usertype.save()
