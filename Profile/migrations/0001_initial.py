# Generated by Django 5.1 on 2024-09-16 20:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=500)),
                ('last_name', models.CharField(blank=True, max_length=500, null=True)),
                ('username', models.CharField(max_length=250, unique=True)),
                ('profile_picture', models.ImageField(upload_to='profile_pic/')),
                ('about_me', models.CharField(max_length=1000)),
                ('followers_count', models.IntegerField(default=0)),
                ('following_count', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='follow_list',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('followers', models.ManyToManyField(related_name='followers_followers', to='Profile.profile')),
                ('following', models.ManyToManyField(related_name='followers_following', to='Profile.profile')),
                ('profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='followers_profile', to='Profile.profile')),
            ],
        ),
    ]
