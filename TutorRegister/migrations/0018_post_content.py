# Generated by Django 5.0.2 on 2024-04-06 07:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("TutorRegister", "0017_post_attachment"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="content",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
    ]
