# Generated by Django 5.0.2 on 2024-04-18 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("TutorRegister", "0026_survey"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="survey",
            name="completed",
        ),
        migrations.AddField(
            model_name="tutoringsession",
            name="survey_completed",
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]