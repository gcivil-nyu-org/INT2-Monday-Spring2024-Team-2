# Generated by Django 5.0.2 on 2024-04-06 05:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("TutorRegister", "0016_profilet_qualified_profilet_transcript_post_reply"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="attachment",
            field=models.FileField(blank=True, null=True, upload_to="attachments/"),
        ),
    ]
