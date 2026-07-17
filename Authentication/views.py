# Standard Library
import re

# Django Core
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login,
    logout,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, redirect

# Local Applications
from .models import Authentication

def Login(request):

    try:

        if request.method == "POST":
            username = request.POST.get('username').strip()
            password = request.POST.get('password').strip()

            user = authenticate(request, username=username, password=password)

            if user is not None:

                login(request, user)
             
                if user.is_superuser:
                    return redirect('Masteradmin_Dashboard')

                try:
                    auth = Authentication.objects.get(user=user)
             
                    if auth.role.lower() == "police":
                        return redirect('Police_Dashboard')

                    elif auth.role.lower() == "civilian":
                        return redirect('Civilian_Dashboard')

                    else:
                        messages.error(request, "Invalid role")
                        return redirect('login')

                except Authentication.DoesNotExist:
                    messages.error(request, "User profile not found")
                    return redirect('login')

            else:
                messages.error(request, "Invalid username or password")
                return redirect('login')

        return render(request, "login.html")

    except Exception as e:
        print("LOGIN ERROR:", e)
        return redirect('Error_Page')   


@login_required
def Masteradmin_Profile_Update(request):

    try:

        redirect_url = 'Masteradmin_Profile_Update'

        user = request.user

        auth, created = Authentication.objects.get_or_create(
            user=user,
            defaults={
                "role": "Admin",
                "full_name": user.username,
                "mobile_number": "",
                "status": True
            }
        )

        if request.method == "POST":

            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            full_name = request.POST.get('full_name', '').strip()
            mobile_number = request.POST.get('mobile_number', '').strip()

            password = request.POST.get('password', '').strip()
            confirm_password = request.POST.get('confirm_password', '').strip()

            profile_image = request.FILES.get('profile_image')

            if not username:
                messages.error(request, "Username is required")
                return redirect(redirect_url)

            if not email:
                messages.error(request, "Email is required")
                return redirect(redirect_url)

            if not full_name:
                messages.error(request, "Full name is required")
                return redirect(redirect_url)

            if not mobile_number:
                messages.error(request, "Mobile number is required")
                return redirect(redirect_url)

            if not re.fullmatch(r'[a-zA-Z0-9_]{4,20}', username):
                messages.error(request, "Invalid username format")
                return redirect(redirect_url)

            if User.objects.filter(username=username).exclude(id=user.id).exists():
                messages.error(request, "Username already exists")
                return redirect(redirect_url)

            if not re.fullmatch(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                messages.error(request, "Enter valid email")
                return redirect(redirect_url)

            if User.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(request, "Email already exists")
                return redirect(redirect_url)

            if Authentication.objects.filter(mobile_number=mobile_number).exclude(user=user).exists():
                messages.error(request, "Mobile number already exists")
                return redirect(redirect_url)

            if not re.fullmatch(r'[0-9]{10}', mobile_number):
                messages.error(request, "Mobile must be 10 digits")
                return redirect(redirect_url)

            if not re.fullmatch(r'[A-Za-z ]{2,50}', full_name):
                messages.error(request, "Invalid name")
                return redirect(redirect_url)

            if password and confirm_password:

                if password != confirm_password:
                    messages.error(request, "Passwords do not match")
                    return redirect(redirect_url)

                pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'

                if not re.match(pattern, password):
                    messages.error(
                        request,
                        "Password must be at least 8 characters long, include uppercase, lowercase, a number, and a special character."
                    )
                    return redirect(redirect_url)

                if user.check_password(password):
                    messages.error(request, "New password cannot be same as old password")
                    return redirect(redirect_url)

            elif password or confirm_password:
                messages.error(request, "Please fill both password fields")
                return redirect(redirect_url)

            try:

                user.username = username
                user.email = email

                if password:
                    user.set_password(password)

                user.save()

                auth.full_name = full_name
                auth.mobile_number = mobile_number

                # CASE 1: Replace image
                if profile_image:
                    if auth.profile_image:
                        auth.profile_image.delete(save=False)
                    auth.profile_image = profile_image

                # CASE 2: Remove image
                elif request.POST.get("remove_profile_image") == "true":
                    if auth.profile_image:
                        auth.profile_image.delete(save=False)
                        auth.profile_image = None

                auth.save()

                if password:
                    logout(request)
                    messages.success(request, "Password updated. Please login again.")
                    return redirect('login')

                messages.success(request, "Profile updated successfully")
                return redirect('Masteradmin_Profile_Management')

            except Exception as e:
                print("UPDATE ERROR:", e)
                messages.error(request, "Something went wrong")
                return redirect(redirect_url)

        return render(request, "masteradmin_profile_update.html", {
            "user": user,
            "auth": auth
        })

    except Exception as e:
        print("GLOBAL ERROR:", e)
        return redirect('Error_Page')


@login_required
def Masteradmin_Civilian_Profile_Registration(request):

    try:

        if request.method == "POST":

            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')
            confirm_password = request.POST.get('confirm_password', '')
            email = request.POST.get('email', '').strip()

            full_name = request.POST.get('full_name', '').strip()
            mobile_number = request.POST.get('mobile_number', '').strip()
            civilian_id_card_name = request.POST.get('civilian_id_card_name', '')

            profile_image = request.FILES.get('profile_image')   
            id_image_front = request.FILES.get('id_image_front')
            id_image_back = request.FILES.get('id_image_back')   

            if not username:
                messages.error(request, "Username is required")
                return redirect('Masteradmin_Civilian_Profile_Registration')

            if not password:
                messages.error(request, "Password is required")
                return redirect('Masteradmin_Civilian_Profile_Registration')

            if not confirm_password:
                messages.error(request, "Confirm password is required")
                return redirect('Masteradmin_Civilian_Profile_Registration')

            if not email:
                messages.error(request, "Email is required")
                return redirect('Masteradmin_Civilian_Profile_Registration')

            if not full_name:
                messages.error(request, "Full name is required")
                return redirect('Masteradmin_Civilian_Profile_Registration')

            if not mobile_number:
                messages.error(request, "Mobile number is required")
                return redirect('Masteradmin_Civilian_Profile_Registration')

            if not civilian_id_card_name:
                messages.error(request, "Please select ID type")
                return redirect('Masteradmin_Civilian_Profile_Registration')

            if not id_image_front:
                messages.error(request, "Front ID image is required")
                return redirect('Masteradmin_Civilian_Profile_Registration')

            if not re.fullmatch(r'[a-zA-Z0-9_]{4,20}', username):
                messages.error(request, "Username must be 4–20 characters and contain only letters, numbers, or underscore")
                return redirect('Masteradmin_Civilian_Profile_Registration')

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists")
                return redirect('Masteradmin_Civilian_Profile_Registration')

            if not re.fullmatch(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                messages.error(request, "Enter a valid email address")
                return redirect('Masteradmin_Civilian_Profile_Registration')

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists")
                return redirect('Masteradmin_Civilian_Profile_Registration')

            if Authentication.objects.filter(mobile_number=mobile_number).exists():
                messages.error(request, "Mobile number already exists")
                return redirect('Masteradmin_Civilian_Profile_Registration')

            if len(password) < 6:
                messages.error(request, "Password must be at least 6 characters")
                return redirect('Masteradmin_Civilian_Profile_Registration')

            if password != confirm_password:
                messages.error(request, "Passwords do not match")
                return redirect('Masteradmin_Civilian_Profile_Registration')

            if not re.fullmatch(r'[0-9]{10}', mobile_number):
                messages.error(request, "Mobile number must be exactly 10 digits")
                return redirect('Masteradmin_Civilian_Profile_Registration')

            if not re.fullmatch(r'[A-Za-z ]{2,50}', full_name):
                messages.error(request, "Full name must contain only letters and spaces")
                return redirect('Masteradmin_Civilian_Profile_Registration')

            try:
       
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email
                )

               
                Authentication.objects.create(
                    user=user,
                    role='Civilian',
                    full_name=full_name,
                    mobile_number=mobile_number,
                    profile_image=profile_image,
                    civilian_id_card_name=civilian_id_card_name,
                    id_image_front=id_image_front,
                    id_image_back=id_image_back,
                    status=True
                )

                messages.success(request, "Registration successful. Please login.")
                return redirect('Masteradmin_Civilian_User')

            except Exception as e:
                print("ERROR:", e)
                messages.error(request, "Something went wrong. Please try again.")
                return redirect('Masteradmin_Civilian_Profile_Registration')

        return render(request, "masteradmin_civilian_profile_registration.html")

    except Exception as e:
        print("GLOBAL ERROR:", e)
        return redirect('Error_Page')


@login_required
def Masteradmin_Civilian_Profile_Update(request, id):

    try:

        def back():
            return redirect('Masteradmin_Civilian_Profile_Update', id=id)

        try:
            user = User.objects.get(id=id)
            auth = Authentication.objects.get(user=user)
        except User.DoesNotExist:
            messages.error(request, "User not found")
            return redirect('Error_Page')
        except Authentication.DoesNotExist:
            messages.error(request, "Profile not found")
            return redirect('Error_Page')

        if request.method == "POST":

            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            full_name = request.POST.get('full_name', '').strip()
            mobile_number = request.POST.get('mobile_number', '').strip()
            status = request.POST.get('status')

            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            profile_image = request.FILES.get('profile_image')

            if not username:
                messages.error(request, "Username is required")
                return back()

            if not email:
                messages.error(request, "Email is required")
                return back()

            if not full_name:
                messages.error(request, "Full name is required")
                return back()

            if not mobile_number:
                messages.error(request, "Mobile number is required")
                return back()

            if not re.fullmatch(r'[a-zA-Z0-9_]{4,20}', username):
                messages.error(request, "Invalid username format")
                return back()

            if User.objects.filter(username=username).exclude(id=user.id).exists():
                messages.error(request, "Username already exists")
                return back()

            if not re.fullmatch(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                messages.error(request, "Enter valid email")
                return back()

            if User.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(request, "Email already exists")
                return back()

            if Authentication.objects.filter(mobile_number=mobile_number).exclude(user=user).exists():
                messages.error(request, "Mobile number already exists")
                return back()

            if not re.fullmatch(r'[0-9]{10}', mobile_number):
                messages.error(request, "Mobile must be 10 digits")
                return back()

            if not re.fullmatch(r'[A-Za-z ]{2,50}', full_name):
                messages.error(request, "Invalid name")
                return back()

            if password or confirm_password:

                if password != confirm_password:
                    messages.error(request, "Passwords do not match")
                    return back()


                pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'

                if not re.match(pattern, password):
                    messages.error(
                        request,
                        "Password must be at least 8 characters long, include uppercase, lowercase, a number, and a special character."
                        )
                    return back()

                if user.check_password(password):
                    messages.error(request, "New password cannot be same as old password")
                    return back()

                user.set_password(password)

            try:

                user.username = username
                user.email = email
                user.save()

                auth.full_name = full_name
                auth.mobile_number = mobile_number

                if status == "Active":
                    auth.status = True
                elif status == "Inactive":
                    auth.status = False

                # CASE 1: Replace image
                if profile_image:
                    if auth.profile_image:
                        auth.profile_image.delete(save=False)
                    auth.profile_image = profile_image

                # CASE 2: Remove image
                elif request.POST.get("remove_profile_image") == "true":
                    if auth.profile_image:
                        auth.profile_image.delete(save=False)
                        auth.profile_image = None

                auth.save()

                if password:
                    messages.success(request, "Password updated successfully")

                messages.success(request, "Profile updated successfully")
                return redirect('Masteradmin_Civilian_User')

            except Exception as e:
                print("UPDATE ERROR:", e)
                messages.error(request, "Something went wrong")
                return back()

        return render(request, "masteradmin_civilian_profile_update.html", {
            "user": user,
            "auth": auth
        })

    except Exception as e:
        print("GLOBAL ERROR:", e)
        return redirect('Error_Page')


def Civilian_Profile_Registration(request):

    try:

        if request.method == "POST":

            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')
            confirm_password = request.POST.get('confirm_password', '')
            email = request.POST.get('email', '').strip()

            full_name = request.POST.get('full_name', '').strip()
            mobile_number = request.POST.get('mobile_number', '').strip()
            civilian_id_card_name = request.POST.get('civilian_id_card_name', '')

            profile_image = request.FILES.get('profile_image')   
            id_image_front = request.FILES.get('id_image_front') 
            id_image_back = request.FILES.get('id_image_back')             

            if not username:
                messages.error(request, "Username is required")
                return redirect('Civilian_Profile_Registration')

            if not password:
                messages.error(request, "Password is required")
                return redirect('Civilian_Profile_Registration')

            if not confirm_password:
                messages.error(request, "Confirm password is required")
                return redirect('Civilian_Profile_Registration')

            if not email:
                messages.error(request, "Email is required")
                return redirect('Civilian_Profile_Registration')

            if not full_name:
                messages.error(request, "Full name is required")
                return redirect('Civilian_Profile_Registration')

            if not mobile_number:
                messages.error(request, "Mobile number is required")
                return redirect('Civilian_Profile_Registration')

            if not civilian_id_card_name:
                messages.error(request, "Please select ID type")
                return redirect('Civilian_Profile_Registration')

            if not id_image_front:
                messages.error(request, "Front ID image is required")
                return redirect('Civilian_Profile_Registration')       

            if not re.fullmatch(r'[a-zA-Z0-9_]{4,20}', username):
                messages.error(request, "Username must be 4–20 characters and contain only letters, numbers, or underscore")
                return redirect('Civilian_Profile_Registration')

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists")
                return redirect('Civilian_Profile_Registration')

            if not re.fullmatch(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                messages.error(request, "Enter a valid email address")
                return redirect('Civilian_Profile_Registration')

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists")
                return redirect('Civilian_Profile_Registration')
            
            if Authentication.objects.filter(mobile_number=mobile_number).exists():
                messages.error(request, "Mobile number already exists")
                return redirect('Civilian_Profile_Registration')


            pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'

            if not re.match(pattern, password):
                messages.error(
                    request,
                    "Password must be at least 8 characters long, include uppercase, lowercase, a number, and a special character."
                    )
                return redirect('Civilian_Profile_Registration')

            if password != confirm_password:
                messages.error(request, "Passwords do not match")
                return redirect('Civilian_Profile_Registration')

            if not re.fullmatch(r'[0-9]{10}', mobile_number):
                messages.error(request, "Mobile number must be exactly 10 digits")
                return redirect('Civilian_Profile_Registration')

            if not re.fullmatch(r'[A-Za-z ]{2,50}', full_name):
                messages.error(request, "Full name must contain only letters and spaces")
                return redirect('Civilian_Profile_Registration')

            try:
               
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email
                )

  
                Authentication.objects.create(
                    user=user,
                    role='Civilian',
                    full_name=full_name,
                    mobile_number=mobile_number,
                    profile_image=profile_image,
                    civilian_id_card_name=civilian_id_card_name,
                    id_image_front=id_image_front,
                    id_image_back=id_image_back,
                    status=True
                )

                messages.success(request, "Registration successful. Please login.")
                return redirect('login')

            except Exception as e:
                print("ERROR:", e)
                messages.error(request, "Something went wrong. Please try again.")
                return redirect('Civilian_Profile_Registration')

        return render(request, "civilian_profile_registration.html")

    except Exception as e:
        print("GLOBAL ERROR:", e)
        return redirect('Error_Page')


@login_required
def Civilian_Profile_Update(request):

    try:

        redirect_url = 'Civilian_Profile_Update'

        user = request.user

        try:
            auth = Authentication.objects.get(user=user)
        except Authentication.DoesNotExist:
            messages.error(request, "Profile not found")
            return redirect('Error_Page')

        if request.method == "POST":

            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            full_name = request.POST.get('full_name', '').strip()
            mobile_number = request.POST.get('mobile_number', '').strip()

            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            profile_image = request.FILES.get('profile_image')

            if not username:
                messages.error(request, "Username is required")
                return redirect(redirect_url)

            if not email:
                messages.error(request, "Email is required")
                return redirect(redirect_url)

            if not full_name:
                messages.error(request, "Full name is required")
                return redirect(redirect_url)

            if not mobile_number:
                messages.error(request, "Mobile number is required")
                return redirect(redirect_url)

            if not re.fullmatch(r'[a-zA-Z0-9_]{4,20}', username):
                messages.error(request, "Invalid username format")
                return redirect(redirect_url)

            if User.objects.filter(username=username).exclude(id=user.id).exists():
                messages.error(request, "Username already exists")
                return redirect(redirect_url)

            if not re.fullmatch(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                messages.error(request, "Enter valid email")
                return redirect(redirect_url)

            if User.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(request, "Email already exists")
                return redirect(redirect_url)

            if Authentication.objects.filter(mobile_number=mobile_number).exclude(user=user).exists():
                messages.error(request, "Mobile number already exists")
                return redirect(redirect_url)

            if not re.fullmatch(r'[0-9]{10}', mobile_number):
                messages.error(request, "Mobile must be 10 digits")
                return redirect(redirect_url)

            if not re.fullmatch(r'[A-Za-z ]{2,50}', full_name):
                messages.error(request, "Invalid name")
                return redirect(redirect_url)

            if password or confirm_password:

                if password != confirm_password:
                    messages.error(request, "Passwords do not match")
                    return redirect(redirect_url)

                pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'

                if not re.match(pattern, password):
                    messages.error(
                        request,
                        "Password must be at least 8 characters long, include uppercase, lowercase, a number, and a special character."
                        )
                    return redirect(redirect_url)

                if user.check_password(password):
                    messages.error(request, "New password cannot be same as old password")
                    return redirect(redirect_url)

                user.set_password(password)

            try:

                user.username = username
                user.email = email
                user.save()

                auth.full_name = full_name
                auth.mobile_number = mobile_number

                # CASE 1: Replace image
                if profile_image:
                    if auth.profile_image:
                        auth.profile_image.delete(save=False)
                    auth.profile_image = profile_image

                # CASE 2: Remove image
                elif request.POST.get("remove_profile_image") == "true":
                    if auth.profile_image:
                        auth.profile_image.delete(save=False)
                        auth.profile_image = None

                auth.save()

                if password:
                    logout(request)
                    messages.success(request, "Password updated. Please login again.")
                    return redirect('Login_Page')

                messages.success(request, "Profile updated successfully")
                return redirect('Civilian_Profile_Management')

            except Exception as e:
                print("UPDATE ERROR:", e)
                messages.error(request, "Something went wrong")
                return redirect(redirect_url)

        return render(request, "civilian_profile_update.html", {
            "user": user,
            "auth": auth
        })

    except Exception as e:
        print("GLOBAL ERROR:", e)
        return redirect('Error_Page')

@login_required
def Masteradmin_Police_Profile_Registration(request):

    try:

        if request.method == "POST":

            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()

            full_name = request.POST.get('full_name', '').strip()
            mobile_number = request.POST.get('mobile_number', '').strip()
            police_id_number = request.POST.get('police_id_number', '').strip()

            profile_image = request.FILES.get('profile_image')
            id_image_front = request.FILES.get('id_image_front')
            id_image_back = request.FILES.get('id_image_back')
     
            if not username:
                messages.error(request, "Username is required")
                return redirect('Masteradmin_Police_Profile_Registration')

            if not email:
                messages.error(request, "Email is required")
                return redirect('Masteradmin_Police_Profile_Registration')

            if not full_name:
                messages.error(request, "Full name is required")
                return redirect('Masteradmin_Police_Profile_Registration')

            if not mobile_number:
                messages.error(request, "Mobile number is required")
                return redirect('Masteradmin_Police_Profile_Registration')

            if not police_id_number:
                messages.error(request, "Police ID is required")
                return redirect('Masteradmin_Police_Profile_Registration')

            if not id_image_front:
                messages.error(request, "Front ID image is required")
                return redirect('Masteradmin_Police_Profile_Registration')
      
            if not re.fullmatch(r'[a-zA-Z0-9_]{4,20}', username):
                messages.error(request, "Invalid username format")
                return redirect('Masteradmin_Police_Profile_Registration')

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists")
                return redirect('Masteradmin_Police_Profile_Registration')

            if not re.fullmatch(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                messages.error(request, "Enter a valid email address")
                return redirect('Masteradmin_Police_Profile_Registration')

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists")
                return redirect('Masteradmin_Police_Profile_Registration')
            
            if Authentication.objects.filter(mobile_number=mobile_number).exists():
                messages.error(request, "Mobile number already exists")
                return redirect('Masteradmin_Police_Profile_Registration')
        
            if Authentication.objects.filter(police_id_number=police_id_number).exists():
                messages.error(request, "Police ID already exists")
                return redirect('Masteradmin_Police_Profile_Registration')

            if not re.fullmatch(r'[0-9]{10}', mobile_number):
                messages.error(request, "Mobile number must be exactly 10 digits")
                return redirect('Masteradmin_Police_Profile_Registration')

            if not re.fullmatch(r'[A-Za-z ]{2,50}', full_name):
                messages.error(request, "Invalid name")
                return redirect('Masteradmin_Police_Profile_Registration')

            try:
           
                user = User.objects.create_user(
                    username=username,
                    email=email
                )

                user.set_unusable_password()
                user.save()

             
                Authentication.objects.create(
                    user=user,
                    role='Police',
                    full_name=full_name,
                    mobile_number=mobile_number,
                    profile_image=profile_image,
                    police_id_number=police_id_number,
                    id_image_front=id_image_front,
                    id_image_back=id_image_back,
                    status=True
                )

                messages.success(
                    request,
                    "Police registered successfully. Please use 'Forgot Password' to set your password."
                )
                return redirect('Masteradmin_Police_User')

            except Exception as e:
                print("ERROR:", e)
                messages.error(request, "Something went wrong")
                return redirect('Masteradmin_Police_Profile_Registration')

        return render(request, "masteradmin_police_profile_registration.html")

    except Exception as e:
        print("GLOBAL ERROR:", e)
        return redirect('Error_Page')

@login_required
def Masteradmin_Police_Profile_Update(request, id):

    try:

        def back():
            return redirect('Masteradmin_Police_Profile_Update', id=id)

        try:
            user = User.objects.get(id=id)
            auth = Authentication.objects.get(user=user)
        except User.DoesNotExist:
            messages.error(request, "User not found")
            return redirect('Error_Page')
        except Authentication.DoesNotExist:
            messages.error(request, "Profile not found")
            return redirect('Error_Page')

        if request.method == "POST":

            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            full_name = request.POST.get('full_name', '').strip()
            mobile_number = request.POST.get('mobile_number', '').strip()
            status = request.POST.get('status')

            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            profile_image = request.FILES.get('profile_image')

            if not username:
                messages.error(request, "Username is required")
                return back()

            if not email:
                messages.error(request, "Email is required")
                return back()

            if not full_name:
                messages.error(request, "Full name is required")
                return back()

            if not mobile_number:
                messages.error(request, "Mobile number is required")
                return back()

            if not re.fullmatch(r'[a-zA-Z0-9_]{4,20}', username):
                messages.error(request, "Invalid username format")
                return back()

            if User.objects.filter(username=username).exclude(id=user.id).exists():
                messages.error(request, "Username already exists")
                return back()

            if not re.fullmatch(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                messages.error(request, "Enter valid email")
                return back()

            if User.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(request, "Email already exists")
                return back()

            if Authentication.objects.filter(mobile_number=mobile_number).exclude(user=user).exists():
                messages.error(request, "Mobile number already exists")
                return back()

            if not re.fullmatch(r'[0-9]{10}', mobile_number):
                messages.error(request, "Mobile must be 10 digits")
                return back()

            if not re.fullmatch(r'[A-Za-z ]{2,50}', full_name):
                messages.error(request, "Invalid name")
                return back()

            if password or confirm_password:

                if password != confirm_password:
                    messages.error(request, "Passwords do not match")
                    return back()
                
                pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'

                if not re.match(pattern, password):
                    messages.error(
                        request,
                        "Password must be at least 8 characters long, include uppercase, lowercase, a number, and a special character."
                    )
                    return back()

                if user.check_password(password):
                    messages.error(request, "New password cannot be same as old password")
                    return back()

                user.set_password(password)

            try:

                user.username = username
                user.email = email
                user.save()

                auth.full_name = full_name
                auth.mobile_number = mobile_number

                if status == "Active":
                    auth.status = True
                elif status == "Inactive":
                    auth.status = False

                # CASE 1: Replace image
                if profile_image:
                    if auth.profile_image:
                        auth.profile_image.delete(save=False)
                    auth.profile_image = profile_image

                # CASE 2: Remove image
                elif request.POST.get("remove_profile_image") == "true":
                    if auth.profile_image:
                        auth.profile_image.delete(save=False)
                        auth.profile_image = None

                auth.save()

                if password:
                    messages.success(request, "Password updated successfully")

                messages.success(request, "Profile updated successfully")
                return redirect('Masteradmin_Police_User')

            except Exception as e:
                print("UPDATE ERROR:", e)
                messages.error(request, "Something went wrong")
                return back()

        return render(request, "masteradmin_police_profile_update.html", {
            "user": user,
            "auth": auth
        })

    except Exception as e:
        print("GLOBAL ERROR:", e)
        return redirect('Error_Page')
    
@login_required
def Police_Profile_Update(request):

    try:

        redirect_url = 'Police_Profile_Update'

        user = request.user

        try:
            auth = Authentication.objects.get(user=user)
        except Authentication.DoesNotExist:
            messages.error(request, "Profile not found")
            return redirect('Error_Page')

        if request.method == "POST":

            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            full_name = request.POST.get('full_name', '').strip()
            mobile_number = request.POST.get('mobile_number', '').strip()

            password = request.POST.get('password', '').strip()
            confirm_password = request.POST.get('confirm_password', '').strip()

            profile_image = request.FILES.get('profile_image')

            if not username:
                messages.error(request, "Username is required")
                return redirect(redirect_url)

            if not email:
                messages.error(request, "Email is required")
                return redirect(redirect_url)

            if not full_name:
                messages.error(request, "Full name is required")
                return redirect(redirect_url)

            if not mobile_number:
                messages.error(request, "Mobile number is required")
                return redirect(redirect_url)

            if not re.fullmatch(r'[a-zA-Z0-9_]{4,20}', username):
                messages.error(request, "Invalid username format")
                return redirect(redirect_url)

            if User.objects.filter(username=username).exclude(id=user.id).exists():
                messages.error(request, "Username already exists")
                return redirect(redirect_url)

            if not re.fullmatch(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                messages.error(request, "Enter valid email")
                return redirect(redirect_url)

            if User.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(request, "Email already exists")
                return redirect(redirect_url)

            if Authentication.objects.filter(mobile_number=mobile_number).exclude(user=user).exists():
                messages.error(request, "Mobile number already exists")
                return redirect(redirect_url)

            if not re.fullmatch(r'[0-9]{10}', mobile_number):
                messages.error(request, "Mobile must be 10 digits")
                return redirect(redirect_url)

            if not re.fullmatch(r'[A-Za-z ]{2,50}', full_name):
                messages.error(request, "Invalid name")
                return redirect(redirect_url)

            if password or confirm_password:

                if password != confirm_password:
                    messages.error(request, "Passwords do not match")
                    return redirect(redirect_url)

                pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'

                if not re.match(pattern, password):
                    messages.error(
                        request,
                        "Password must be at least 8 characters long, include uppercase, lowercase, a number, and a special character."
                    )
                    return redirect(redirect_url)

                if user.check_password(password):
                    messages.error(request, "New password cannot be same as old password")
                    return redirect(redirect_url)

            try:

                user.username = username
                user.email = email

                if password:
                    user.set_password(password)

                user.save()

                auth.full_name = full_name
                auth.mobile_number = mobile_number

                # CASE 1: Replace image    
                if profile_image:
                    if auth.profile_image:
                        auth.profile_image.delete(save=False)
                    auth.profile_image = profile_image

                # CASE 2: Remove image
                elif request.POST.get("remove_profile_image") == "true":
                    if auth.profile_image:
                        auth.profile_image.delete(save=False)
                        auth.profile_image = None

                auth.save()

                if password:
                    logout(request)
                    messages.success(request, "Password updated. Please login again.")
                    return redirect('Login_Page')

                messages.success(request, "Profile updated successfully")
                return redirect('Police_Profile_Management')

            except Exception as e:
                print("UPDATE ERROR:", e)
                messages.error(request, "Something went wrong")
                return redirect(redirect_url)

        return render(request, "police_profile_update.html", {
            "user": user,
            "auth": auth
        })

    except Exception as e:
        print("GLOBAL ERROR:", e)
        messages.error(request, "Something went wrong. Please try again.")
        return redirect('Error_Page')

@login_required 
def Delete_User_Profile(request, id):

    try:

        try:
            user = User.objects.get(id=id)
            auth = Authentication.objects.get(user=user)
        except User.DoesNotExist:
            messages.error(request, "User not found")
            return redirect('Error_Page')
        except Authentication.DoesNotExist:
            messages.error(request, "User profile not found")
            return redirect('Error_Page')

        role = auth.role.lower()
        is_self_delete = (request.user.id == user.id)

        if not request.user.is_superuser and not is_self_delete:
            messages.error(request, "Unauthorized access")
            return redirect('Error_Page')

        # 🔹 Delete profile related images
        if auth.profile_image:
            auth.profile_image.delete(save=False)

        if auth.id_image_front:
            auth.id_image_front.delete(save=False)

        if auth.id_image_back:
            auth.id_image_back.delete(save=False)

        # 🔥 ADD THIS BLOCK (ONLY NEW PART)
        from Civilian_User.models import Evidence

        evidences = Evidence.objects.filter(user=user)

        for e in evidences:
            if e.image1:
                e.image1.delete(save=False)
            if e.image2:
                e.image2.delete(save=False)
            if e.image3:
                e.image3.delete(save=False)

        # 🔥 Delete user (will cascade delete DB records)
        user.delete()

        # 🔥 SELF DELETE → logout + login page
        if is_self_delete:
            logout(request)
            messages.success(request, "Your account has been deleted")
            return redirect('login')

        # 🔥 SUPERADMIN DELETE CIVILIAN
        if request.user.is_superuser and role == "civilian":
            messages.success(request, "Civilian user deleted successfully")
            return redirect('Masteradmin_Civilian_User')

        # 🔥 SUPERADMIN DELETE POLICE
        if request.user.is_superuser and role == "police":
            messages.success(request, "Police user deleted successfully")
            return redirect('Masteradmin_Police_User')

        messages.error(request, "Invalid role")
        return redirect('Error_Page')

    except Exception as e:
        print("DELETE ERROR:", e)
        return redirect('Error_Page')


def Forgot_Password(request):

    try:

        if request.method == "POST":

            username = request.POST.get('username', '').strip()
            mobile_number = request.POST.get('mobile_number', '').strip()

            if not username:
                messages.error(request, "Username is required")
                return redirect('Forgot_Password')

            if not mobile_number:
                messages.error(request, "Mobile number is required")
                return redirect('Forgot_Password')

            try:
                user = User.objects.get(username=username)
                auth = Authentication.objects.get(user=user)

                if auth.mobile_number != mobile_number:
                    messages.error(request, "Mobile number does not match")
                    return redirect('Forgot_Password')
               
                request.session['reset_user_id'] = user.id

                return redirect('Reset_Password')

            except User.DoesNotExist:
                messages.error(request, "Username not found")
                return redirect('Forgot_Password')

            except Authentication.DoesNotExist:
                messages.error(request, "User profile not found")
                return redirect('Forgot_Password')

        return render(request, "forgot_password.html")

    except Exception as e:
        print("FORGOT PASSWORD ERROR:", e)
        return redirect('Error_Page')

def Reset_Password(request):

    try:

        user_id = request.session.get('reset_user_id')

        if not user_id:
            messages.error(request, "Session expired. Please verify your account again.")
            return redirect('Forgot_Password')

        if request.method == "POST":

            password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if not password:
                messages.error(request, "Please enter a new password.")
                return redirect('Reset_Password')           
          
            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return redirect('Reset_Password')

            pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'

            if not re.match(pattern, password):
                messages.error(
                    request,
                    "Password must be at least 8 characters long, include uppercase, lowercase, a number, and a special character."
                )
                return redirect('Reset_Password')
            
            try:
                user = User.objects.get(id=user_id)

                # ✅ FIXED: moved here (after user is defined)
                if user.check_password(password):
                    messages.error(request, "New password cannot be same as old password")
                    return redirect('Reset_Password')

                if check_password(password, user.password):
                    messages.error(request, "New password cannot be the same as your previous password.")
                    return redirect('Reset_Password')

                user.password = make_password(password)
                user.save()

                del request.session['reset_user_id']

                messages.success(request, "Password updated successfully. Please login with your new password.")
                return redirect('login')

            except User.DoesNotExist:
                messages.error(request, "User not found.")
                return redirect('Forgot_Password')

            except Exception as e:
                print("RESET ERROR:", e)
                messages.error(request, "Something went wrong. Please try again.")
                return redirect('Reset_Password')

        return render(request, "reset_password.html")

    except Exception as e:
        print("GLOBAL RESET ERROR:", e)
        return redirect('Error_Page')

def Logout(request):
    try:
        if request.method == "POST":

            if request.user.is_authenticated:
                logout(request)
                messages.success(request, "Logged out successfully.")
                return redirect('login')
            else:
                messages.warning(request, "You are not logged in.")
                return redirect('login')

        messages.error(request, "Invalid request method.")
        return redirect('Error_Page')

    except Exception as e:
        print("LOGOUT ERROR:", e)
        messages.error(request, "Something went wrong during logout.")
        return redirect('Error_Page')


def Error_Page(request):
    return render(request, "error_page.html")