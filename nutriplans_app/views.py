from pyexpat.errors import messages
from django.shortcuts import render,redirect
from django.http import HttpResponse
from grpc import Status
from numpy import block
from nutriplans_app.forms import CustomUserCreationForm ,AddClients
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User
from django.contrib import auth
from .forms import AddMeasurements, EditEquivalents, SignUpForm
from django.contrib import messages
from .models import Clients,Measurements,Equivalents
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group
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

        #get user_id
        login_user_id=request.user.id

        # get all clients from current user
        client_list = Clients.objects.all().filter(user_id=login_user_id)
        
        # get addpatientform
        add_client_form=AddClients()

        if request.method == 'POST':
            #add new client
            if request.POST.get('action_button')=='add_button':
                print('add client time')
                add_client_form = AddClients(request.POST)
                if add_client_form.is_valid():
                    print('time to save')
                    # load the profile instance created by the signal
                    name=request.POST['name']
                    status=request.POST['status']
                    gender=request.POST['gender']
                    birthday=request.POST['birthday']
                    age=request.POST['age']
                    height=request.POST['height']
                    target_weight=request.POST['target_weight']
                    email=request.POST['email']
                    phone=request.POST['phone']
                    address=request.POST['address']

                    new_client=Clients.objects.create(name=name,status=status,gender=gender,birthday=birthday, age=age, height=height,target_weight=target_weight,email=email,phone=phone,address=address,user_id=request.user.id )
                    new_client.save()
                    messages.success(request,''+name+' has been added! If you want to see ')

                    
                    # create equiv for new client
                    new_equiv = Equivalents(client_id=new_client.id,target_calories=0.0,carbohydrates_percent=40,proteins_percent=30,fat_percent=30,full_milk=0,semi_milk=0,zero_milk=0,fruits=0,vegetables=0,bread_cereals=0,full_meat=0,semi_meat=0,zero_meat=0,fat=0)
                    new_equiv.save()
                    
                    return render(request, 'workspace.html',{'client_list':client_list,'target_row':-1,'add_client_form':add_client_form})  

                else:
                    print('not valid')
                    openmodal='add_patient_modal'
                    return render(request, 'workspace.html',{'client_list':client_list,'target_row':-1,'add_client_form':add_client_form, 'openmodal':openmodal}) 

            if request.POST.get('action_button')=='view_client_page':
                #action="{% url 'client_page' field.user_id field.id %}"
                print ('redirect')
                target_client_id=request.POST['target_row']
                return redirect('client_page',client_id=target_client_id)

            if request.POST.get('action_button')=='delete_client':
                
                target_client_id=request.POST['target_row']
                print ('delete ',target_client_id)

                #get name fo delete client                
                target_client=Clients.objects.all().filter(id=target_client_id)
                target_client_name=target_client[0].name

                #delete target client
                Clients.objects.all().filter(id=target_client_id).delete()

                #get updated client list
                client_list = Clients.objects.all().filter(user_id=login_user_id)

                messages.success(request,''+target_client_name+' has been deleted!')

                return render(request, 'workspace.html',{'client_list':client_list,'add_client_form':add_client_form})
            
        else:
            return render(request, 'workspace.html',{'client_list':client_list,'add_client_form':add_client_form})  
    else:

        Sign_up_form = SignUpForm()
        
        return render(request, 'index.html',{'Sign_up_form': Sign_up_form, 'openmodal':'signin','messages_signin':'you must login first'}) 


@group_required('Nutrition')
def client_page(request,client_id):

    login_user_id=request.user.id
    print('id= ',client_id)
    target_client_id=client_id

    #get info client
    target_client = Clients.objects.all().filter(id=target_client_id)
    edit_client=AddClients(initial={'name':target_client[0].name,'status':target_client[0].status,'gender':target_client[0].gender,'birthday':target_client[0].birthday,'age':target_client[0].age,'height':target_client[0].height,'target_weight':target_client[0].target_weight,'email':target_client[0].email,'phone':target_client[0].phone,'address':target_client[0].address})

    client_measurements = Measurements.objects.all().order_by('-date').filter(client_id=target_client_id)
    add_measurment_form = AddMeasurements()


    client_equiv= Equivalents.objects.all().filter(client_id=client_id)
    edit_equiv=EditEquivalents(initial={'target_calories':client_equiv[0].target_calories,'carbohydrates_percent':client_equiv[0].carbohydrates_percent,'proteins_percent':client_equiv[0].proteins_percent,'fat_percent':client_equiv[0].fat_percent,'full_milk':client_equiv[0].full_milk,'semi_milk':client_equiv[0].semi_milk,'zero_milk':client_equiv[0].zero_milk,'fruits':client_equiv[0].fruits,'vegetables':client_equiv[0].vegetables,'bread_cereals':client_equiv[0].bread_cereals,'full_meat':client_equiv[0].full_meat,'semi_meat':client_equiv[0].semi_meat,'zero_meat':client_equiv[0].zero_meat,'fat':client_equiv[0].fat})

    # client data id user whant to edit
    
    #measurements data for chart
    data = serializers.serialize("json",Measurements.objects.all().order_by('date').filter(client_id=client_id))
    equiv_data = serializers.serialize("json",Equivalents.objects.all().filter(client_id=client_id))

    if request.method == 'POST':
        if request.POST.get('action_button')=='edit_client_info':
            print('edit time')
                    
            return render(request, 'client_page.html',{'target_client':target_client,'client_measurements':client_measurements,'edit_client':edit_client,'action_info':'edit','add_measurment_form':add_measurment_form})
        
        if request.POST.get('action_button')=='save_client_info':
            print('save time')
            edit_client = AddClients(request.POST)
            
            if edit_client.is_valid():
                print('time to save')
                # load the profile instance created by the signal
                name=request.POST['name']
                status=request.POST['status']
                gender=request.POST['gender']
                birthday=request.POST['birthday']
                age=request.POST['age']
                height=request.POST['height']
                target_weight=request.POST['target_weight']
                email=request.POST['email']
                phone=request.POST['phone']
                address=request.POST['address']

                Clients.objects.filter(id=client_id).update(name=name,status=status,gender=gender,birthday=birthday, age=age, height=height,target_weight=target_weight,email=email,phone=phone,address=address,)

                messages.success(request,''+name+' has been updated! If you want to see ')
                target_client = Clients.objects.all().filter(id=client_id)
                return render(request, 'client_page.html',{'target_client':target_client,'client_measurements':client_measurements,'edit_client':edit_client,'action_info':'show'})
            else:
                print('not valid')
                
                return render(request, 'client_page.html',{'target_client':target_client, 'edit_client': edit_client,'client_measurements':client_measurements,'edit_client':edit_client,'openmodal':'edit_client_modal'})
    
        #############################################################
        if request.POST.get('action_button')=='add_measurements_button':
            print('add measurment time')
            add_measurment_form = AddMeasurements(request.POST)
            if add_measurment_form.is_valid():
                print('time to save')
                
                # load the profile instance created by the signal
                date=request.POST['date']
                activity_factor=request.POST['activity_factor']
                weight=request.POST['weight']
                fat=request.POST['fat']
                muscle_mass=request.POST['muscle_mass']
                bone_mass=request.POST['bone_mass']
                liquids=request.POST['liquids']
                vinceral_fat=request.POST['vinceral_fat']
                Measurements.objects.create(client_id=client_id,date=date,activity_factor=activity_factor,weight=weight,fat=fat,muscle_mass=muscle_mass,bone_mass=bone_mass,liquids=liquids,vinceral_fat=vinceral_fat)
                
                messages.success(request,'measurment to '+target_client[0].name+' has been added!')
                #update measurements
                client_measurements = Measurements.objects.all().order_by('-date').filter(client_id=client_id)
                data = serializers.serialize("json",Measurements.objects.all().order_by('date').filter(client_id=client_id))

                return render(request, 'client_page.html',{'target_client':target_client,'add_measurment_form':add_measurment_form,'client_measurements':client_measurements,'action_info':'show','data':data})  

            else:
                print('not valid')
                client_measurements = Measurements.objects.all().order_by('-date').filter(client_id=login_user_id)
                return render(request, 'client_page.html',{'target_client':target_client,'client_measurements':client_measurements,'edit_client':edit_client,'action_info':'show','add_measurment_form':add_measurment_form,'data':data,'openmodal':'add_measurements_modal'})
        
        if request.POST.get('action_button')=='delete_client_button':

            target_mes_id=request.POST['target_row']
            print ('delete ',target_mes_id)
            #get name fo delete client                

            Measurements.objects.all().filter(id=target_mes_id).delete()
            #get updated client list
            client_list = Clients.objects.all().filter(user_id=login_user_id)
            messages.success(request,'A mesurement has been deleted!')
            data = serializers.serialize("json",Measurements.objects.all().order_by('date').filter(client_id=client_id))

            return render(request, 'client_page.html',{'target_client':target_client,'client_measurements':client_measurements,'edit_client':edit_client,'action_info':'show','add_measurment_form':add_measurment_form,'data':data})

        if request.POST.get('action_button')=='edit_measurements_button':
            
            target_mes_id=request.POST['target_row']
            print ('edit ',target_mes_id)
            #get name fo delete client                

            edit_mes=Measurements.objects.all().filter(id=target_mes_id)
            edit_measurement_form = AddMeasurements(initial={'id':edit_mes[0].id,'date': edit_mes[0].date,'activity_factor': edit_mes[0].activity_factor,'weight': edit_mes[0].weight,'fat': edit_mes[0].fat,'muscle_mass': edit_mes[0].muscle_mass,'bone_mass': edit_mes[0].bone_mass,'liquids':edit_mes[0].liquids,'vinceral_fat':edit_mes[0].vinceral_fat,'client_id':edit_mes[0].client_id})
            return render(request, 'client_page.html',{'target_client':target_client,'client_measurements':client_measurements,'edit_client':edit_client,'action_info':'show','add_measurment_form':add_measurment_form,'data':data,'edit_measurement_form':edit_measurement_form,'openmodal':'edit_measurements_modal','target_mes_id':target_mes_id})

        if request.POST.get('action_button')=='edit_save_measurements_button':
            print('update measurment time')
            update_measurment_form = AddMeasurements(request.POST)
            if update_measurment_form.is_valid():
                print('time to update')
                
                # load the profile instance created by the signal
                date=request.POST['date']
                activity_factor=request.POST['activity_factor']
                weight=request.POST['weight']
                fat=request.POST['fat']
                muscle_mass=request.POST['muscle_mass']
                bone_mass=request.POST['bone_mass']
                liquids=request.POST['liquids']
                vinceral_fat=request.POST['vinceral_fat']

                Measurements.objects.filter(id=request.POST['target_mes_id']).update(client_id=client_id,date=date,activity_factor=activity_factor,weight=weight,fat=fat,muscle_mass=muscle_mass,bone_mass=bone_mass,liquids=liquids,vinceral_fat=vinceral_fat)
                
                messages.success(request,'measurement has been updated!')
                #update measurements
                client_measurements = Measurements.objects.all().order_by('-date').filter(client_id=client_id)
                data = serializers.serialize("json",Measurements.objects.all().order_by('date').filter(client_id=client_id))

                return render(request, 'client_page.html',{'target_client':target_client,'add_measurment_form':add_measurment_form,'client_measurements':client_measurements,'action_info':'show','data':data})  

            else:
                print('not valid')
                edit_mes=Measurements.objects.all().filter(id=request.POST['target_mes_id'])
                edit_measurement_form = AddMeasurements(initial={'id':target_mes_id,'date': edit_mes[0].date,'activity_factor': edit_mes[0].activity_factor,'weight': edit_mes[0].weight,'fat': edit_mes[0].fat,'muscle_mass': edit_mes[0].muscle_mass,'bone_mass': edit_mes[0].bone_mass,'liquids':edit_mes[0].liquids,'vinceral_fat':edit_mes[0].vinceral_fat,'client_id':edit_mes[0].client_id})
                return render(request, 'client_page.html',{'target_client':target_client,'client_measurements':client_measurements,'edit_client':edit_client,'action_info':'show','add_measurment_form':add_measurment_form,'data':data,'edit_measurement_form':edit_measurement_form,'openmodal':'edit_measurements_modal'})

        if request.POST.get('action_button')=='save_equivalents_modal_button':
            print('save equivalents')
            edit_equiv = EditEquivalents(request.POST)
            
            if edit_equiv.is_valid():
                print('time to save equiv')
                
                target_calories=request.POST.get('target_calories')
                if target_calories=='':
                    target_calories=0.0
                
                carbohydrates_percent=request.POST.get('carbohydrates_percent')
                if carbohydrates_percent=='':
                    carbohydrates_percent=0

                proteins_percent=request.POST.get('proteins_percent')
                if proteins_percent=='':
                    proteins_percent=0
                
                fat_percent=request.POST.get('fat_percent')
                if fat_percent=='':
                    fat_percent=0
                
                full_milk=request.POST.get('full_milk')
                if full_milk=='':
                    full_milk=0

                semi_milk=request.POST.get('semi_milk')
                if semi_milk=='':
                    semi_milk=0

                zero_milk=request.POST.get('zero_milk')
                if zero_milk=='':
                    zero_milk=0
                    
                fruits=request.POST.get('fruits')
                if fruits=='':
                    fruits=0

                vegetables=request.POST.get('vegetables')
                if vegetables=='':
                    vegetables=0

                bread_cereals=request.POST.get('bread_cereals')
                if bread_cereals=='':
                    bread_cereals=0

                full_meat=request.POST.get('full_meat')
                if full_meat=='':
                    full_meat=0

                semi_meat=request.POST.get('semi_meat')
                if semi_meat=='':
                    semi_meat=0

                zero_meat=request.POST.get('zero_meat')
                if zero_meat=='':
                    zero_meat=0

                fat=request.POST.get('fat')
                if fat=='':
                    fat=0
                
                Equivalents.objects.filter(client_id=client_id).update(target_calories=target_calories,carbohydrates_percent=carbohydrates_percent,proteins_percent=proteins_percent,fat_percent=fat_percent, full_milk=full_milk, semi_milk=semi_milk,zero_milk=zero_milk,fruits=fruits,vegetables=vegetables,bread_cereals=bread_cereals,full_meat=full_meat,semi_meat=semi_meat,zero_meat=zero_meat,fat=fat)

                messages.success(request,'Equivalents has been updated!')
                client_equiv= Equivalents.objects.all().filter(client_id=client_id)
                equiv_data = serializers.serialize("json",Equivalents.objects.all().filter(client_id=client_id))
                return render(request, 'client_page.html',{'target_client':target_client,'client_measurements':client_measurements,'action_info':'show','add_measurment_form':add_measurment_form,'data':data,'client_equiv':client_equiv,'edit_equiv':edit_equiv})
            else:
                print('not valid')
                messages.warning(request,'Equivalents has Not been updated!')
                return render(request, 'client_page.html',{'target_client':target_client,'client_measurements':client_measurements,'edit_client':edit_client,'action_info':'edit'})
    

    print('lets go')


    return render(request, 'client_page.html',{'target_client':target_client,'edit_client':edit_client,'client_measurements':client_measurements,'add_measurment_form':add_measurment_form,'data':data,'client_equiv':client_equiv,'edit_equiv':edit_equiv,'equiv_data':equiv_data})

