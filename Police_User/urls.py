from django.urls import path
from .views import *

urlpatterns = [
   
    path('Police_Dashboard/', Police_Dashboard, name='Police_Dashboard'),
    path('Police_Evidence_History/', Police_Evidence_History, name='Police_Evidence_History'),
    path('Police_Evidence_Review_Process/<int:id>/', Police_Evidence_Review_Process, name='Police_Evidence_Review_Process'),
    path('Police_Evidence_View/<int:id>/', Police_Evidence_View, name='Police_Evidence_View'),
    path('Police_Profile_Management/', Police_Profile_Management, name='Police_Profile_Management'),
    
]