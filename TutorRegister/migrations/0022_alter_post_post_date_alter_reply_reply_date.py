# Generated by Django 5.0.2 on 2024-04-08 18:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("TutorRegister", "0021_merge_20240408_1526"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="post_date",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="reply",
            name="reply_date",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
