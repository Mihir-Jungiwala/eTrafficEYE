from django.shortcuts import redirect
from django.contrib import messages
from Authentication.models import Authentication

class Authorization_Middleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        path = request.path.lower()

        if (
            path.startswith('/static') or
            path.startswith('/media') or
            path == '/' or
            path.startswith('/login') or
            path.startswith('/admin/login') or
            path.startswith('/logout') or
            path.startswith('/delete_user_profile')
        ):
            return self.get_response(request)

        if not request.user.is_authenticated:
            return self.get_response(request)

        user = request.user

        if user.is_superuser:
            if path.startswith('/masteradmin_') or path.startswith('/admin'):
                return self.get_response(request)
            else:
                messages.error(request, "Admin access only.")
                return redirect('Masteradmin_Dashboard')

        try:
            auth = Authentication.objects.get(user=user)
        except Authentication.DoesNotExist:
            messages.error(request, "User role not found.")
            return redirect('Error_Page')

        role = auth.role.lower()

        if role == "civilian":
            if path.startswith('/civilian_'):
                return self.get_response(request)
            else:
                messages.error(request, "Access denied.")
                return redirect('Civilian_Dashboard')

        elif role == "police":
            if path.startswith('/police_'):
                return self.get_response(request)
            else:
                messages.error(request, "Access denied.")
                return redirect('Police_Dashboard')

        messages.error(request, "Unauthorized access.")
        return redirect('login')