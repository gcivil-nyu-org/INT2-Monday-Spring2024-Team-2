# Generated by Django 5.0.2 on 2024-04-11 18:54

import django.contrib.postgres.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("TutorRegister", "0022_alter_post_post_date_alter_reply_reply_date"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="topics",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(), blank=True, default=[], size=None
            ),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name="React",
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
                ("like", models.BooleanField()),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="post_react",
                        to="TutorRegister.post",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_react",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]