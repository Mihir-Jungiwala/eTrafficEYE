from django.urls import path
from .views import *

urlpatterns = [
   
    path('Civilian_Dashboard/', Civilian_Dashboard, name='Civilian_Dashboard'),
    path('Civilian_Evidence_Upload/', Civilian_Evidence_Upload, name='Civilian_Evidence_Upload'),
    path('Civilian_Evidence_History/', Civilian_Evidence_History, name='Civilian_Evidence_History'),
    path('Civilian_Evidence_View/<int:id>/', Civilian_Evidence_View, name='Civilian_Evidence_View'),
    path('Civilian_Profile_Management/', Civilian_Profile_Management, name='Civilian_Profile_Management'),
    
]