# Django Core
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect

# Local Applications
from Authentication.models import Authentication
from Civilian_User.models import Evidence
from Police_User.models import Police_Evidence_Review

@login_required
def Civilian_Dashboard(request):

    try:
        if not request.user.is_authenticated:
            messages.error(request, "Please login to continue.")
            return redirect('Login_Page')

        user = request.user

        try:
            auth = Authentication.objects.get(user=user)
        except Authentication.DoesNotExist:
            auth = None

        if auth and auth.full_name:
            full_name = auth.full_name
        else:
            full_name = user.username

        evidences = Evidence.objects.filter(user=user)

        total_uploaded = evidences.count()

        approved = 0
        rejected = 0
        pending = 0

        for ev in evidences:

            review = Police_Evidence_Review.objects.filter(
                evidence=ev
            ).order_by('-id').first()

            if review:
                status = review.status.lower()

                if status == "approved":
                    approved += 1
                elif status == "rejected":
                    rejected += 1
                else:
                    pending += 1
            else:
                pending += 1

        return render(request, "civilian_dashboard.html", {
            "user": user,
            "auth": auth,
            "full_name": full_name,
            "total_uploaded": total_uploaded,
            "approved": approved,
            "rejected": rejected,
            "pending": pending
        })

    except Exception as e:
        print("ERROR (Civilian_Dashboard):", e)
        messages.error(request, "Something went wrong.")
        return redirect('Error_Page')


@login_required
def Civilian_Evidence_Upload(request):

    try:

        last = Evidence.objects.order_by('-complaint_seq').first()

        if last:
            next_seq = last.complaint_seq + 1
        else:
            next_seq = 1

        next_number = f"CMP-{next_seq:05d}"

        if request.method == "POST":

            address = request.POST.get('address', '').strip()
            city = request.POST.get('city', '').strip()
            state = request.POST.get('state', '').strip()
            pincode = request.POST.get('pincode', '').strip()
            country = request.POST.get('country', '').strip()
            datetime_val = request.POST.get('datetime')
            vehicle_number = request.POST.get('vehicle_number', '').strip()
            description = request.POST.get('description', '').strip()
            violations = request.POST.get('violations', '').strip()

            images = request.FILES.getlist('images')

            if not address:
                messages.error(request, "Address is required")
                return redirect('Civilian_Evidence_Upload')

            if not images:
                messages.error(request, "At least one image is required")
                return redirect('Civilian_Evidence_Upload')

            if len(images) > 3:
                messages.error(request, "Maximum 3 images allowed")
                return redirect('Civilian_Evidence_Upload')

            try:

                with transaction.atomic():

                    evidence = Evidence.objects.create(
                        user=request.user,
                        complaint_no=next_number,
                        complaint_seq=next_seq,
                        address=address,
                        city=city,
                        state=state,
                        pincode=pincode,
                        country=country,
                        datetime=datetime_val,
                        vehicle_number=vehicle_number,
                        description=description,
                        violations=violations
                    )

                    if len(images) >= 1:
                        evidence.image1 = images[0]

                    if len(images) >= 2:
                        evidence.image2 = images[1]

                    if len(images) >= 3:
                        evidence.image3 = images[2]

                    evidence.save()

                messages.success(request, "Evidence uploaded successfully")
                return redirect('Civilian_Evidence_History')

            except Exception as e:
                print("SAVE ERROR:", e)
                messages.error(request, "Something went wrong")
                return redirect('Civilian_Evidence_Upload')

        return render(request, "civilian_evidence_upload.html", {
            "complaint_number": next_number
        })

    except Exception as e:
        print("GLOBAL ERROR:", e)
        return redirect('Error_Page')

@login_required
def Civilian_Evidence_History(request):

    try:
   
        if not request.user.is_authenticated:
            messages.error(request, "Please login to continue.")
            return redirect('Login_Page')

        evidences = Evidence.objects.filter(
            user=request.user
        ).order_by('-id')

        for ev in evidences:
            ev.review = Police_Evidence_Review.objects.filter(
                evidence=ev
            ).order_by('-id').first()

        return render(request, "civilian_evidence_history.html", {
            "evidences": evidences
        })

    except Exception as e:
        print("ERROR (Civilian_Evidence_History):", e)
        messages.error(request, "Something went wrong. Please try again later.")
        return redirect('Error_Page')


@login_required
def Civilian_Evidence_View(request, id): 

    try:

        if not request.user.is_authenticated:
            messages.error(request, "Please login to access this page.")
            return redirect('Login_Page')

        evidence = Evidence.objects.filter(
            id=id,
            user=request.user
        ).first()

        if not evidence:
            messages.error(request, "Requested evidence not found or access denied.")
            return redirect('Civilian_Evidence_History')

        review = Police_Evidence_Review.objects.filter(
            evidence=evidence
        ).order_by('-id').first()

        auth = None
        if review:
            try:
                from Authentication.models import Authentication
                auth = Authentication.objects.get(user=review.police)
            except Authentication.DoesNotExist:
                auth = None

        return render(request, "civilian_evidence_view.html", {
            "evidence": evidence,
            "review": review,  
            "auth": auth    
        })

    except Exception as e:
        print("ERROR (Civilian_Evidence_View):", e)
        messages.error(request, "An unexpected error occurred. Please try again later.")
        return redirect('Error_Page')
    

@login_required
def Civilian_Profile_Management(request):

    try:
        user = request.user

        try:
            auth = Authentication.objects.get(user=user)
        except Authentication.DoesNotExist:
            auth = None

        return render(request, "civilian_profile_management.html", {
            "user": user,
            "auth": auth
        })

    except Exception as e:
        print("ERROR:", e)
        return redirect('Error_Page')
    



