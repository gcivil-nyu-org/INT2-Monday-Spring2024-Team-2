# Generated by Django 5.0.2 on 2024-03-07 23:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("TutorRegister", "0004_usertype"),
    ]

    operations = [
        migrations.AddField(
            model_name="usertype",
            name="has_profile_complete",
            field=models.BooleanField(default=False),
        ),
    ]