"""
URL configuration for AquaGuard_Django project.
...
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import LogoutView
from django.shortcuts import render # <--- IMPORT RENDER
from django.contrib.sitemaps.views import sitemap
from .sitemaps import PublicViewSitemap

# View for Service Worker (renders with context from processors)
def service_worker(request):
    # We pass the request to render_to_string to make sure
    # context processors (like your Firebase keys) are included.
    content = render_to_string('sw.js', request=request)
    return HttpResponse(content, content_type='application/javascript')

# View for Manifest (renders with context for static paths)
def manifest(request):
    # We pass the request to render to make sure
    # the {% static %} template tag works correctly.
    return render(request, 'manifest.json', content_type='application/json')

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

# Sitemap configuration
sitemaps = {
    'public': PublicViewSitemap,
}

urlpatterns = [
    path('sw.js', service_worker, name='service_worker'),
    path('manifest.json', manifest, name='manifest'), # <--- ADD THIS LINE
    path('firebase-messaging-sw.js', firebase_service_worker, name='firebase_service_worker'),
    path('admin/logout/', AdminLogoutView.as_view(), name='admin_logout'),
    path('AquaSavvy-Control/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('', include('dashboard.urls')),
]