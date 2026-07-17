from django.urls import path
from .views import *

urlpatterns = [
    path('', Login, name='login'),

    path('Masteradmin_Profile_Update/', Masteradmin_Profile_Update, name='Masteradmin_Profile_Update'),

    path('Masteradmin_Civilian_Profile_Registration/', Masteradmin_Civilian_Profile_Registration, name='Masteradmin_Civilian_Profile_Registration'),
     path('Masteradmin_Civilian_Profile_Update/<int:id>/', Masteradmin_Civilian_Profile_Update, name='Masteradmin_Civilian_Profile_Update'),
    path('Civilian_Profile_Registration/', Civilian_Profile_Registration, name='Civilian_Profile_Registration'),
    path('Civilian_Profile_Update/', Civilian_Profile_Update, name='Civilian_Profile_Update'),

    path('Masteradmin_Police_Profile_Registration/', Masteradmin_Police_Profile_Registration, name='Masteradmin_Police_Profile_Registration'),
    path('Masteradmin_Police_Profile_Update/<int:id>/', Masteradmin_Police_Profile_Update, name='Masteradmin_Police_Profile_Update'),
    path('Police_Profile_Update/', Police_Profile_Update, name='Police_Profile_Update'),

    path('Delete_User_Profile/<int:id>/', Delete_User_Profile, name='Delete_User_Profile'),

    path('Forgot_Password/', Forgot_Password, name='Forgot_Password'),
    path('Reset_Password/', Reset_Password, name='Reset_Password'),
    path('Logout/', Logout, name='Logout'),

    path('Error_Page/', Error_Page, name='Error_Page'),

]