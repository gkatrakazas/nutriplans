from pickle import READONLY_BUFFER
from tokenize import group
from django import forms  
from django.contrib.auth.models import User, Permission, Group
from django.contrib.auth.forms import UserCreationForm  
from django.core.exceptions import ValidationError  
from django.forms.fields import EmailField  
from django.forms.forms import Form  
from django.db import models
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator 

from nutriplans_app.models import Clients, Equivalents, Clients




class CustomUserCreationForm(UserCreationForm):  
    username = forms.CharField(label='username', min_length=5, max_length=150)  
    email = forms.EmailField(label='email')  
    password1 = forms.CharField(label='password', widget=forms.PasswordInput)  
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)  
  
    def username_clean(self):  
        username = self.cleaned_data['username'].lower()  
        new = User.objects.filter(username = username)  
        if new.count():  
            raise ValidationError("User Already Exist")  
        return username  
  
    def email_clean(self):  
        email = self.cleaned_data['email'].lower()  
        new = User.objects.filter(email=email)  
        if new.count():  
            raise ValidationError(" Email Already Exist")  
        return email  
  
    def clean_password2(self):
        if self.data['password'] != self.data['password2']:
            raise forms.ValidationError('Passwords are not the same')
        return self.data['password']

        password1 = self.cleaned_data['password1']  
        password2 = self.cleaned_data['password2']  
   
  
    def save(self, commit = True):  
        print("User created")
        user = User.objects.create_user(  
            self.cleaned_data['username'],  
            self.cleaned_data['email'],  
            self.cleaned_data['password1']  
        )  
        return user  

class SignUpForm(UserCreationForm):
    username = forms.CharField(label="Username", required=True,widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Username'}))
    first_name = forms.CharField(label="First Name", required=True,widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'First Name'}), max_length=32, help_text='First name')
    last_name = forms.CharField(label="Last Name", required=True,widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Last Name'}), max_length=32, help_text='Last name')
    email = forms.EmailField(label="Email", required=True,widget=forms.EmailInput(attrs={'class': 'form-control','placeholder': 'email'}), max_length=64, help_text='Enter a valid email address')
    password1 = forms.CharField(label="Password", required=True,widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'Password'}))
    password2 = forms.CharField(label="Password Again", required=True,widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'Password Again'}))

    class Meta:
        model = User
        fields = ('username','first_name','last_name','email', 'password1', 'password2', )
        
    def clean_password2(self):

        print ('i am in')
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2 


from functools import partial

DateInput = partial(forms.DateInput, {'class': 'datepicker'})

class AddClients(forms.Form):
    status_choices = (
        ('Active', 'Active'),
        ('Active', 'Inactive'),
    )
    gender_choices = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    
    name = forms.CharField(label="Name", required=True,max_length=32,widget=forms.TextInput(attrs={'class': 'form-control','onChange':'validate_then_submit()','onkeyup' : "validate_then_submit();",'placeholder': 'full name'}))
    status = forms.ChoiceField(label="Status", required=True,choices=status_choices,widget=forms.Select(attrs={'class':'form-control','onChange':'validate_then_submit()','onkeyup' : "validate_then_submit();"}))
    gender= forms.ChoiceField(label="Gender", required=True,choices=gender_choices,widget=forms.Select(attrs={'class':'form-control','onChange':'validate_then_submit()','onkeyup' : "validate_then_submit();"}))
    birthday = forms.DateField(label="Birthday", required=True,widget=forms.DateInput(attrs={'type': 'date','class':'form-control','onchange' : "find_age();" "validate_then_submit()",'onkeyup' :"find_age();" "validate_then_submit();"}))
    age = forms.IntegerField(label="Age",required=True,widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'age auto fill by birthday date','onChange':'validate_then_submit()'}))
    height = forms.IntegerField(label="Height",required=True,validators=[MaxValueValidator(300),MinValueValidator(0)],widget=forms.NumberInput(attrs={'class': 'form-control','onChange':'validate_then_submit()','placeholder': 'height in cm'}))
    initial_weight = forms.FloatField(label="Initial Weight",required=True,validators=[MaxValueValidator(500.0),MinValueValidator(0.0)],widget=forms.NumberInput(attrs={'class': 'form-control','onChange':'validate_then_submit()','placeholder': 'initial weight'}))
    target_weight = forms.FloatField(label="Target Weight",required=True,validators=[MaxValueValidator(500.0),MinValueValidator(0.0)],widget=forms.NumberInput(attrs={'class': 'form-control','onChange':'validate_then_submit()','placeholder': 'target weight'}))
    email = forms.EmailField(label="Email", required=True,widget=forms.EmailInput(attrs={'class': 'form-control','onChange':'validate_then_submit()','placeholder': 'email'}), max_length=64)
    phone = forms.IntegerField(label="Phone Number", required=False,widget=forms.NumberInput(attrs={'class': 'form-control','onChange':'validate_then_submit()','placeholder': 'phone number (optional)'}))
    address = forms.CharField(label="Adress", required=False, max_length=100,widget=forms.TextInput(attrs={'class': 'form-control','onChange':'validate_then_submit()','placeholder': 'address (optional)'}))
    notes = forms.CharField(label="Notes", required=False, max_length=500,widget=forms.Textarea(attrs={'class': 'form-control','onChange':'validate_then_submit()','placeholder': 'notes (optional)'}))
    
    def __str__(self):
            return self.name

    #def clean_email(self):
    #    email = self.cleaned_data.get('email')
    #        if Patients.objects.filter(email=email).exists():
    #        raise forms.ValidationError("Email is already exists")



    class Meta:
        model = Clients
        fields = ('name','status','gender','birthday', 'age', 'height','target_weight','email','phone','address' )


class AddMeasurements(forms.Form):
    
    date = forms.DateField(label="Date", required=True,widget=forms.DateInput(attrs={'type': 'date','class':'form-control'}))
    activity_factor = forms.FloatField(label="Activity Factor",required=True,validators=[MaxValueValidator(3.0),MinValueValidator(1.0)],widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'activity factor'}))
    weight = forms.FloatField(label="Weight",required=True,validators=[MaxValueValidator(500.0),MinValueValidator(0.0)],widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'weight'}))    
    fat = forms.FloatField(label="Fat",validators=[MaxValueValidator(100.0),MinValueValidator(0.0)],widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'fat %'}))
    muscle_mass = forms.FloatField(label="Muscle mass",validators=[MaxValueValidator(100.0),MinValueValidator(0.0)],widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'muscle mass %'}))
    bone_mass = forms.FloatField(label="Bone mass",validators=[MaxValueValidator(100.0),MinValueValidator(0.0)],widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'bone mass %'}))
    liquids = forms.FloatField(label="Liquids",validators=[MaxValueValidator(100.0),MinValueValidator(0.0)],widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'liquids %'}))
    vinceral_fat = forms.FloatField(label="Vinceral fat",validators=[MaxValueValidator(100.0),MinValueValidator(0.0)],widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'vinceral fat %'}))

    def __str__(self):
            return self.date

    class Meta:
        model = Clients
        fields = ('date','weight','fat','muscle_mass', 'bone_mass', 'liquids','vinceral_fat')


class EditEquivalents(forms.Form):
    target_calories = forms.FloatField(label="Target Calories",required=True,validators=[MinValueValidator(0.0)],widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'target calories'}))
    carbohydrates_percent = forms.IntegerField(label="Carbohydrates %",required=True,validators=[MinValueValidator(0)],widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'carbohydrates %'}))
    proteins_percent= forms.IntegerField(label="Proteins %",required=True,validators=[MinValueValidator(0)],widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'proteins %'}))
    fat_percent= forms.IntegerField(label="Fat %",required=True,validators=[MinValueValidator(0)],widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'fat %'}))
    full_milk = forms.IntegerField(label="Full Milk",required=True,validators=[MinValueValidator(0)],widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'full milk','onkeyup' : "updateequiv();",'onChange' : "updateequiv();"}))
    semi_milk = forms.IntegerField(label="Semi Milk",required=True,validators=[MinValueValidator(0)],widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'semi milk','onkeyup' : "updateequiv();",'onChange' : "updateequiv();"}))
    zero_milk = forms.IntegerField(label="zero Milk",required=True,validators=[MinValueValidator(0)],widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'zero milk','onkeyup' : "updateequiv();",'onChange' : "updateequiv();"}))
    fruits = forms.IntegerField(label="Fruits",required=True,validators=[MinValueValidator(0)],widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'fruits','onkeyup' : "updateequiv();",'onChange' : "updateequiv();"}))
    vegetables = forms.IntegerField(label="Vegetables",required=True,validators=[MinValueValidator(0)],widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'vegetables','onkeyup' : "updateequiv();",'onChange' : "updateequiv();"}))
    bread_cereals = forms.IntegerField(label="Bread/Cereals",required=True,validators=[MinValueValidator(0)],widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'bread/cereals','onkeyup' : "updateequiv();",'onChange' : "updateequiv();"}))
    full_meat = forms.IntegerField(label="Full Meat",required=True,validators=[MinValueValidator(0)],widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'full meat','onkeyup' : "updateequiv();",'onChange' : "updateequiv();"}))
    semi_meat = forms.IntegerField(label="Semi Meat",required=True,validators=[MinValueValidator(0)],widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'semi meat','onkeyup' : "updateequiv();",'onChange' : "updateequiv();"}))
    zero_meat = forms.IntegerField(label="Zero Meat",required=True,validators=[MinValueValidator(0)],widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'zero meat','onkeyup' : "updateequiv();",'onChange' : "updateequiv();"}))
    fat = forms.IntegerField(label="Fat",required=True,validators=[MinValueValidator(0)],widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'fat'}))

    def __str__(self):
        return self.target_calories

    class Meta:
        model = Equivalents
        fields = ('target_calories','carbohydrates_percent','proteins_percent','fat_percent', 'full_milk', 'semi_milk','zero_milk','fruits','vegetables','bread_cereals','full_meat','semi_meat','zero_meat','fat')

