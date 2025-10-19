"""
URL configuration for AquaGuard_Django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect

def service_worker(request):
    content = render_to_string('sw.js')
    return HttpResponse(content, content_type='application/javascript')

def firebase_service_worker(request):
    try:
        with open('firebase-messaging-sw.js', 'r') as f:
            content = f.read()
        return HttpResponse(content, content_type='application/javascript')
    except FileNotFoundError:
        return HttpResponse('// Firebase service worker not found', content_type='application/javascript')

# Custom admin logout view
class AdminLogoutView(LogoutView):
    next_page = 'public_home'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            print(f"🔒 Admin user '{request.user.username}' logged out")
        return super().dispatch(request, *args, **kwargs)

urlpatterns = [
    path('sw.js', service_worker, name='service_worker'),
    path('firebase-messaging-sw.js', firebase_service_worker, name='firebase_service_worker'),
    path('admin/logout/', AdminLogoutView.as_view(), name='admin_logout'),
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
]
