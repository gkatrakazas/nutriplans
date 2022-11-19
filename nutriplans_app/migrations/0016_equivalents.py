# Generated by Django 4.0.5 on 2022-07-08 17:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nutriplans_app', '0015_remove_patients_current_weight_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Equivalents',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target_Calories', models.FloatField(default=0.0)),
                ('carbohydrates_percent', models.IntegerField(default=40)),
                ('proteins_percent', models.IntegerField(default=30)),
                ('fat_percent', models.IntegerField(default=30)),
                ('full_milk', models.IntegerField(default=0)),
                ('semi_milk', models.IntegerField(default=0)),
                ('zero_milk', models.IntegerField(default=0)),
                ('fruits', models.IntegerField(default=0)),
                ('vegetables', models.IntegerField(default=0)),
                ('bread_cereals', models.IntegerField(default=0)),
                ('full_meat', models.IntegerField(default=0)),
                ('semi_meat', models.IntegerField(default=0)),
                ('zero_meat', models.IntegerField(default=0)),
                ('fat', models.IntegerField(default=0)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nutriplans_app.patients')),
            ],
        ),
    ]