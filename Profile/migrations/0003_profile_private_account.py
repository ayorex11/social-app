# Generated by Django 5.1 on 2024-09-17 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0002_alter_profile_about_me_alter_profile_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='private_account',
            field=models.BooleanField(default=False),
        ),
    ]
