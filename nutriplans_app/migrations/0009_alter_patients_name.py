# Generated by Django 4.0.5 on 2022-06-28 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutriplans_app', '0008_μeasurements'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patients',
            name='name',
            field=models.CharField(default='', max_length=32, verbose_name='Name'),
        ),
    ]
