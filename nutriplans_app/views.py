from pyexpat.errors import messages
from django.shortcuts import render,redirect
from django.http import HttpResponse
from grpc import Status
from numpy import block
from nutriplans_app.forms import CustomUserCreationForm ,AddPatients
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User
from django.contrib import auth
from .forms import AddMeasurements, SignUpForm
from django.contrib import messages
from .models import Patients,Measurements
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group
from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {message_constants.DEBUG: 'debug',
                message_constants.INFO: 'info',
                message_constants.SUCCESS: 'success',
                message_constants.WARNING: 'warning',
                message_constants.ERROR: 'danger',}

from django.core import serializers


def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
        return False

    return user_passes_test(in_groups, login_url='403')


def index(request):
    print(request.user)
    form = SignUpForm()
    return render(request, 'index.html',{'form': form})  


# Create your views here.

def signin(request):
    print( 'signin')
    if request.method == 'POST': 
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        print(user,username,password)
        if user is not None:
            login(request, user)
            if request.user.is_authenticated:
                print('is_authenticated')

                print()
                
                return redirect('workspace')
        else:
            return render(request, 'index.html',{'openmodal' : 'singin_modal','messages_signin':'username or password in wrong'}) 
    else:
         return render(request, 'index.html',{'openmodal' : 'singin_modal','messages_signin':'you must login first'}) 

def logout(request):
    print('logged out')
    auth.logout(request)

    return redirect('index')

        
# Create your views here.


def signup(request):
    print('try signup')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():

            print('is valid')
            user = form.save()
            user.refresh_from_db()  
            # load the profile instance created by the signal
            user.save()
            raw_password = form.cleaned_data.get('password1')
 
            # login user after signing up
            user = authenticate(username=user.username, password=raw_password)
            nutrition_group = Group.objects.get(name='Nutrition') 
            nutrition_group.user_set.add(user)

            login(request, user)
 
            # redirect user to home page
            return render(request, 'workspace.html',{'form': form})  
        else:
            openmodal='signup'
            return render(request, 'index.html',{'form': form, 'openmodal':openmodal}) 
    else:
        print('no valid')
        form = SignUpForm()
    return render(request, 'base.html', {'form': form})


@group_required('Nutrition')
def workspace(request):
    if request.user.is_authenticated:

        login_user_id=request.user.id

        # get all clients from current user
        client_list = Patients.objects.all().filter(user_id=login_user_id)
        
        # get true or false if exists records
        #record_exist=Patients.objects.filter().exists()
        
        add_client_form=AddPatients()
        if request.method == 'POST':
            #add new client
            if request.POST.get('action_button')=='add_button':
                print('add client time')
                add_client_form = AddPatients(request.POST)
                if add_client_form.is_valid():
                    print('time to save')
                    # load the profile instance created by the signal
                    name=request.POST['name']
                    status=request.POST['status']
                    gender=request.POST['gender']
                    birthday=request.POST['birthday']
                    age=request.POST['age']
                    height=request.POST['height']
                    current_weight=request.POST['current_weight']
                    target_weight=request.POST['target_weight']
                    email=request.POST['email']
                    phone=request.POST['phone']
                    address=request.POST['address']

                    Patients.objects.create(name=name,status=status,gender=gender,birthday=birthday, age=age, height=height,current_weight=current_weight,target_weight=target_weight,email=email,phone=phone,address=address,user_id=request.user.id )
                    messages.success(request,''+name+' has been added! If you want to see  ')
                    
                    return render(request, 'workspace.html',{'client_list':client_list,'target_row':-1,'add_client_form':add_client_form})  

                else:
                    print('not valid')
                    openmodal='add_patient_modal'
                    return render(request, 'workspace.html',{'client_list':client_list,'target_row':-1,'add_client_form':add_client_form, 'openmodal':openmodal}) 

            if request.POST.get('action_button')=='view_client_page':
                #action="{% url 'client_page' field.user_id field.id %}"
                print ('redirect')
                target_client=request.POST['target_row']
                return redirect('client_page',client_id=target_client)
            #view client page

        return render(request, 'workspace.html',{'client_list':client_list,'add_client_form':add_client_form})  
    else:
        Sign_up_form = SignUpForm()
        return render(request, 'index.html',{'Sign_up_form': Sign_up_form, 'openmodal':'signin'}) 


@group_required('Nutrition')
def client_page(request,client_id):

    print('id= ',client_id)
    target_row=client_id

    #get info client
    target_client = Patients.objects.all().filter(id=client_id)
    client_measurements = Measurements.objects.all().order_by('-date').filter(patient=target_row)
    add_measurment_form = AddMeasurements()

    # client data id user whant to edit
    edit_client = AddPatients(initial={'id':target_client[0].id,'name': target_client[0].name,'status': target_client[0].status,'gender': target_client[0].gender,'birthday': target_client[0].birthday,'age': target_client[0].age,'height': target_client[0].height,'current_weight': target_client[0].current_weight,'target_weight':target_client[0].current_weight,'target_weight':target_client[0].target_weight,'email':target_client[0].email,'phone':target_client[0].phone,'address':target_client[0].address})
    
    #measurements data for chart
    data = serializers.serialize("json",Measurements.objects.all().order_by('date').filter(patient=client_id))

    if request.method == 'POST':
        if request.POST.get('action_button')=='edit_client_info':
            print('edit time')
            edit_client = AddPatients(initial={'id':target_client[0].id,'name': target_client[0].name,'status': target_client[0].status,'gender': target_client[0].gender,'birthday': target_client[0].birthday,'age': target_client[0].age,'height': target_client[0].height,'current_weight': target_client[0].current_weight,'target_weight':target_client[0].current_weight,'target_weight':target_client[0].target_weight,'email':target_client[0].email,'phone':target_client[0].phone,'address':target_client[0].address})
            
            return render(request, 'client_page.html',{'target_client':target_client,'client_measurements':client_measurements,'edit_client':edit_client,'action_info':'edit','add_measurment_form':add_measurment_form})
        
        if request.POST.get('action_button')=='save_client_info':
            print('save time')
            edit_client = AddPatients(request.POST)
            
            if edit_client.is_valid():
                print('time to save')
                # load the profile instance created by the signal
                name=request.POST['name']
                status=request.POST['status']
                gender=request.POST['gender']
                birthday=request.POST['birthday']
                age=request.POST['age']
                height=request.POST['height']
                current_weight=request.POST['current_weight']
                target_weight=request.POST['target_weight']
                email=request.POST['email']
                phone=request.POST['phone']
                address=request.POST['address']

                
                Patients.objects.filter(id=client_id).update(name=name,status=status,gender=gender,birthday=birthday, age=age, height=height,current_weight=current_weight,target_weight=target_weight,email=email,phone=phone,address=address,)

                messages.success(request,''+name+' has been updated! If you want to see ')
                target_client = Patients.objects.all().filter(id=target_row)
                return render(request, 'client_page.html',{'target_client':target_client,'client_measurements':client_measurements,'edit_client':edit_client,'action_info':'show'})
            else:
                print('not valid')
                return render(request, 'client_page.html',{'target_client':target_client,'client_measurements':client_measurements,'edit_client':edit_client,'action_info':'edit'})
    
        #############################################################
        if request.POST.get('action_button')=='add_measurements_button':
            print('add measurment time')
            add_measurment_form = AddMeasurements(request.POST)
            if add_measurment_form.is_valid():
                print('time to save')
                
                # load the profile instance created by the signal
                date=request.POST['date']
                weight=request.POST['weight']
                fat=request.POST['fat']
                muscle_mass=request.POST['muscle_mass']
                bone_mass=request.POST['bone_mass']
                liquids=request.POST['liquids']
                vinceral_fat=request.POST['vinceral_fat']
                Measurements.objects.create(patient_id=client_id,date=date,weight=weight,fat=fat,muscle_mass=muscle_mass,bone_mass=bone_mass,liquids=liquids,vinceral_fat=vinceral_fat)
                messages.success(request,'measurment to '+target_client[0].name+' has been added!')

                client_measurements = Measurements.objects.all().filter(patient=target_row)
                return render(request, 'client_page.html',{'target_client':target_client,'add_measurment_form':add_measurment_form,'client_measurements':client_measurements,'action_info':'show'})  

            else:
                print('not valid')
                openmodal='add_patient_modal'

    else:
    
        return render(request, 'client_page.html',{'target_client':target_client,'client_measurements':client_measurements,'edit_client':edit_client,'action_info':'show','add_measurment_form':add_measurment_form,'data':data})

