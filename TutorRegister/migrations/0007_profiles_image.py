# Generated by Django 5.0.2 on 2024-03-08 20:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("TutorRegister", "0006_alter_profilet_salary_max_alter_profilet_salary_min"),
    ]

    operations = [
        migrations.AddField(
            model_name="profiles",
            name="image",
            field=models.ImageField(
                default="images/profile_icon.png", upload_to="images/"
            ),
        ),
    ]