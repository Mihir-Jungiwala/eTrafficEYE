from django.urls import path
from .views import *

urlpatterns = [
   
    path('Masteradmin_Dashboard/', Masteradmin_Dashboard, name='Masteradmin_Dashboard'),
    path('Masteradmin_Civilian_User/', Masteradmin_Civilian_User, name='Masteradmin_Civilian_User'),
    path('Masteradmin_Police_User/', Masteradmin_Police_User, name='Masteradmin_Police_User'),
    path('Masteradmin_Profile_Management/', Masteradmin_Profile_Management, name='Masteradmin_Profile_Management'),  
    
]