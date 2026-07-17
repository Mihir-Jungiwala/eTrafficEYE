# Django Core
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

# Local Applications
from Authentication.models import Authentication

@login_required
def Masteradmin_Dashboard(request):

    try:
        from django.contrib.auth.models import User
        from Civilian_User.models import Evidence
        from Police_User.models import Police_Evidence_Review
        from Authentication.models import Authentication

        if not request.user.is_authenticated:
            messages.error(request, "Please login to continue.")
            return redirect('Login_Page')

        user = request.user

        try:
            auth = Authentication.objects.get(user=user)
        except Authentication.DoesNotExist:
            auth = None

        total_users = User.objects.filter(is_superuser=False).count()

        civilian_total = Authentication.objects.filter(role__iexact="civilian").count()
        police_total = Authentication.objects.filter(role__iexact="police").count()

        civilian_active = Authentication.objects.filter(
            role__iexact="civilian", status=True
        ).count()

        civilian_inactive = Authentication.objects.filter(
            role__iexact="civilian", status=False
        ).count()

        police_active = Authentication.objects.filter(
            role__iexact="police", status=True
        ).count()

        police_inactive = Authentication.objects.filter(
            role__iexact="police", status=False
        ).count()

        total_cases = Evidence.objects.count()

        # ✅ STATUS COUNTS
        approved = Police_Evidence_Review.objects.filter(
            status__iexact="approved"
        ).count()

        rejected = Police_Evidence_Review.objects.filter(
            status__iexact="rejected"
        ).count()

        pending = total_cases - (approved + rejected)

        rewards_count = Police_Evidence_Review.objects.filter(
            status__iexact="approved",
            reward_amount__gt=0
        ).count()

        return render(request, "masteradmin_dashboard.html", {
            "user": user,
            "auth": auth,

            "total_users": total_users,
            "total_cases": total_cases,

            "civilian_total": civilian_total,
            "civilian_active": civilian_active,
            "civilian_inactive": civilian_inactive,

            "police_total": police_total,
            "police_active": police_active,
            "police_inactive": police_inactive,

            "approved": approved,
            "rejected": rejected,
            "pending": pending,
            "rewards_count": rewards_count
        })

    except Exception as e:
        print("ERROR (Masteradmin_Dashboard):", e)
        messages.error(request, "Something went wrong.")
        return redirect('Error_Page')


@login_required
def Masteradmin_Civilian_User(request):

    try:
        civilians = Authentication.objects.filter(role__iexact="Civilian")

        return render(request, "masteradmin_civilian_user.html", {
            "civilians": civilians
        })

    except Exception as e:
        print("ERROR:", e)
        return redirect('Error_Page')


@login_required
def Masteradmin_Police_User(request):

    try:
        police = Authentication.objects.filter(role__iexact="Police")

        return render(request, "masteradmin_police_user.html", {
            "police": police
        })

    except Exception as e:
        print("ERROR:", e)
        return redirect('Error_Page')


@login_required
def Masteradmin_Profile_Management(request):

    try:
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

        return render(request, "masteradmin_profile_management.html", {
            "user": user,
            "auth": auth
        })

    except Exception as e:
        print("ERROR:", e)
        return redirect('Error_Page')









