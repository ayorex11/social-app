# Generated by Django 5.1 on 2024-10-14 12:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0002_rename_body_message_encrypted_body'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ['-date_created']},
        ),
    ]
