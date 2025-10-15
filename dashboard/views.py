# dashboard/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.views import View
from .models import Device

# --- NEW: VIEW FOR THE PUBLIC HOMEPAGE ---
def public_home_view(request):
    """
    This is the new public-facing homepage that Google will see.
    """
    return render(request, 'public_home.html')

# --- MODIFIED: THIS VIEW NOW REDIRECTS USERS ---
def home_view(request):
    """
    This view now redirects logged-in users to their device list,
    and logged-out users to the new public homepage.
    """
    if request.user.is_authenticated:
        return redirect('device_list')
    return redirect('public_home') # Redirect to the new public page

@login_required
def device_list_view(request):
    devices = Device.objects.filter(owner=request.user)
    return render(request, 'device_list.html', {'devices': devices})

@login_required
def dashboard_view(request, device_id):
    device = get_object_or_404(Device, device_id=device_id, owner=request.user)
    last_reading = device.readings.order_by('-timestamp').first()
    return render(request, 'dashboard.html', {'device': device, 'last_reading': last_reading})

class CustomLoginView(LoginView):
    template_name = 'login.html'

class CustomLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')