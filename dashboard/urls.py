# dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('devices/', views.device_list_view, name='device_list'),
    path('dashboard/<str:device_id>/', views.dashboard_view, name='dashboard'),
    
    # --- CHANGE: The root path now points to the new public home_view ---
    path('', views.home_view, name='public_home'), 
    path('home/', views.home_view, name='public_home_alias'), # Alias for 'home'

    # --- NEW: API URLs FOR CHAT AND AUTOMATION ---
    path('api/ai_chat/', views.gemini_chat_proxy, name='gemini_chat_proxy'),
    path('api/ai_chat_public/', views.gemini_public_chat, name='gemini_public_chat'),
    path('api/save_rule/', views.save_automation_rule, name='save_automation_rule'),
    path('api/delete_rule/', views.delete_automation_rule, name='delete_automation_rule'),
]