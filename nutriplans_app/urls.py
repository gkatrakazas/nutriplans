import django
from django.urls import path,include,re_path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('signup', views.signup, name = 'signup'), 
    path('signin', views.signin, name = 'signin'), 
    path('logout', views.logout, name = 'logout'), 
    path('',include("django.contrib.auth.urls")), 
    path('workspace', views.workspace, name = 'workspace'), 
    path('client_page/<int:user_id>/<int:client_id>/', views.client_page, name = 'client_page'), 
    


]