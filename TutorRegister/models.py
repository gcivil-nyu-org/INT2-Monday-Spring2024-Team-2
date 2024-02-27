from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Expertise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    level = models.CharField(max_length=255)

class Availability(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=255)
    start_time = models.TimeField()
    end_time = models.TimeField()

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
    salary_min = models.IntegerField()
    salary_max = models.IntegerField()

class UserType(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=100, null=True, blank=True)

# Signal to automatically create or update UserType when a User instance is saved
@receiver(post_save, sender=User)
def create_or_update_user_type(sender, instance, created, **kwargs):
    if created:
        UserType.objects.create(user=instance)
    instance.usertype.save()