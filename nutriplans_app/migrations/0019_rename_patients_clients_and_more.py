# Generated by Django 4.0.5 on 2022-07-09 07:09

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('nutriplans_app', '0018_rename_target_calories_equivalents_target_calories'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Patients',
            new_name='Clients',
        ),
        migrations.RenameField(
            model_name='measurements',
            old_name='patient',
            new_name='client',
        ),
    ]
