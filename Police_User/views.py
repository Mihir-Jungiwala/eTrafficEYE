# Django Core
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

# Local Applications
from Authentication.models import Authentication
from Civilian_User.models import Evidence
from Police_User.models import Police_Evidence_Review

@login_required
def Police_Dashboard(request):

    try:
  
        if not request.user.is_authenticated:
            messages.error(request, "Please login to continue.")
            return redirect('Login_Page')

        user = request.user
    
        try:
            auth = Authentication.objects.get(user=user)
        except Authentication.DoesNotExist:
            auth = None
      
        evidences = Evidence.objects.all()

        total_cases = evidences.count()

        approved = 0
        pending = 0
        rejected = 0

        for ev in evidences:
            review = Police_Evidence_Review.objects.filter(
                evidence=ev
            ).order_by('-id').first()

            if review:
                if review.status == "approved":
                    approved += 1
                elif review.status == "rejected":
                    rejected += 1
                else:
                    pending += 1
            else:
                pending += 1

        return render(request, "police_dashboard.html", {
            "user": user,
            "auth": auth,               
            "total_cases": total_cases,
            "approved": approved,
            "pending": pending,
            "rejected": rejected
        })

    except Exception as e:
        print("ERROR (Police_Dashboard):", e)
        messages.error(request, "Something went wrong.")
        return redirect('Error_Page')


@login_required
def Police_Evidence_History(request):

    try:
        evidences = Evidence.objects.all().order_by('-id')

        for ev in evidences:
            ev.review = Police_Evidence_Review.objects.filter(
                evidence=ev
            ).order_by('-id').first()

        return render(request, "police_evidence_history.html", {
            "evidences": evidences
        })

    except Exception as e:
        print("ERROR:", e)
        return redirect('Error_Page')


@login_required
def Police_Evidence_Review_Process(request, id): 

    try:

        if not request.user.is_authenticated:
            messages.error(request, "Please login to continue.")
            return redirect('Login_Page')

        evidence = Evidence.objects.filter(id=id).first()

        if not evidence:
            messages.error(request, "Evidence not found.")
            return redirect('Police_Evidence_History')

        fine_map = {
            "Helmet Violation": 500,
            "Signal Jump": 1000,
            "Wrong Parking": 300,
            "Over Speeding": 1500,
            "No Seatbelt": 500,
            "Mobile Usage": 1000,
            "Illegal U-Turn": 700,
            "Drunk Driving": 5000
        }

        if request.method == "POST":

            try:
                selected = []
                total = 0

                violations = evidence.violations.split(",")

                for i, v in enumerate(violations):
                    name = v.strip()

                    if request.POST.get(f"violation_{i}") == "on":
                        selected.append(name)
                        total += fine_map.get(name, 0)

                remark = request.POST.get("remark", "").strip()
                action = request.POST.get("action")

                if action not in ["approve", "reject"]:
                    messages.error(request, "Invalid action.")
                    return redirect(request.path)

                if action == "approve":

                    if not selected:
                        messages.error(request, "Please select at least one violation.")
                        return redirect(request.path)

                    reward = int(total * 0.10)
                    status = "approved"

                else:
                    total = 0
                    reward = 0
                    selected = []
                    status = "rejected"

                Police_Evidence_Review.objects.create(
                    evidence=evidence,
                    police=request.user,
                    selected_violations=",".join(selected),
                    penalty_amount=total,
                    reward_amount=reward,
                    remark=remark,
                    status=status
                )

                messages.success(request, "Evidence reviewed successfully.")
                return redirect('Police_Evidence_History')

            except Exception as form_error:
                print("FORM ERROR:", form_error)
                messages.error(request, "Error while processing the form.")
                return redirect('Error_Page')

        return render(request, "police_evidence_review.html", {
            "evidence": evidence
        })

    except Exception as e:
        print("MAIN ERROR:", e)
        messages.error(request, "Something went wrong. Please try again later.")
        return redirect('Error_Page')


@login_required
def Police_Evidence_View(request, id): 

    try:

        if not request.user.is_authenticated:
            messages.error(request, "Please login to access this page.")
            return redirect('Login_Page')

        evidence = Evidence.objects.filter(id=id).first()
      
        if not evidence:
            messages.error(request, "Requested evidence does not exist.")
            return redirect('Police_Evidence_History')
      
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

        return render(request, "police_evidence_view.html", {
            "evidence": evidence,
            "review": review,   
            "auth": auth      
        })

    except Exception as e:
        print("ERROR (Police_Evidence_View):", e)
        messages.error(request, "An unexpected error occurred. Please try again later.")
        return redirect('Error_Page')
    

@login_required
def Police_Profile_Management(request):

    try:
        user = request.user

        try:
            auth = Authentication.objects.get(user=user)
        except Authentication.DoesNotExist:
            auth = None

        return render(request, "police_profile_management.html", {
            "user": user,
            "auth": auth
        })

    except Exception as e:
        print("ERROR:", e)
        return redirect('Error_Page')
    
