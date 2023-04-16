from ctypes.wintypes import tagRECT
import imp
from django.db import models
from django import forms
import datetime
from django.contrib.auth.models import User, Permission, Group
from zmq import DEALER

#nutrition_group, created = Group.objects.get_or_create(name="Nutrition")
#client_group, created = Group.objects.get_or_create(name="Client")

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
   

from six import text_type

class Clients(models.Model):
    status_choices = (
        ('Active', 'Active'),
        ('Active', 'Inactive'),
    )
    gender_choices = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(default='',max_length=32)
    status = models.CharField(max_length=7,choices=status_choices)
    gender= models.CharField(max_length=7,choices=gender_choices)
    birthday = models.CharField(default='',max_length=100)
    age = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    # initial_weight = models.IntegerField(default=0)
    target_weight = models.IntegerField(default=0.0)
    email = models.EmailField(default='')
    phone = models.IntegerField(default=0)
    address = models.CharField(default='',max_length=100)
    # notes = models.CharField(default='',max_length=1000)

    def __str__(self):
        return self.name



class Measurements(models.Model):
    client = models.ForeignKey(Clients, on_delete=models.CASCADE)
    date = models.CharField(default='',max_length=100)
    activity_factor = models.FloatField(default=1.0)
    weight = models.FloatField(default=0.0)
    fat= models.FloatField(default=0.0)
    muscle_mass = models.FloatField(default=0.0)
    bone_mass = models.FloatField(default=0.0)
    liquids = models.FloatField(default=0.0)
    vinceral_fat = models.FloatField(default=0.0)


    def __str__(self):
        return self.date




class Equivalents(models.Model):
    client = models.ForeignKey(Clients, on_delete=models.CASCADE)
    target_calories = models.FloatField(default=0.0)
    carbohydrates_percent = models.IntegerField(default=40)
    proteins_percent= models.IntegerField(default=30)
    fat_percent= models.IntegerField(default=30)
    full_milk = models.IntegerField(default=0)
    semi_milk = models.IntegerField(default=0)
    zero_milk = models.IntegerField(default=0)
    fruits = models.IntegerField(default=0)
    vegetables = models.IntegerField(default=0)
    bread_cereals = models.IntegerField(default=0)
    full_meat = models.IntegerField(default=0)
    semi_meat = models.IntegerField(default=0)
    zero_meat = models.IntegerField(default=0)
    fat = models.IntegerField(default=0)
    
    def __str__(self):
        return self.client
