# Generated by Django 5.0.2 on 2024-04-17 14:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("TutorRegister", "0025_vote_delete_react"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Survey",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("q1", models.BooleanField(blank=True, null=True)),
                ("q2", models.BooleanField(blank=True, null=True)),
                ("q3", models.BooleanField(blank=True, null=True)),
                (
                    "completed",
                    models.BooleanField(blank=True, default=False, null=True),
                ),
                (
                    "reviewee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_reviewee",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "reviewer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_reviewer",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="session_survey",
                        to="TutorRegister.tutoringsession",
                    ),
                ),
            ],
        ),
    ]