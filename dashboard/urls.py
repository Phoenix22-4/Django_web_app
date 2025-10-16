# dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # --- ADD THIS NEW URL PATTERN FOR THE PUBLIC PAGE ---
    path('home/', views.public_home_view, name='public_home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('devices/', views.device_list_view, name='device_list'),
    path('dashboard/<str:device_id>/', views.dashboard_view, name='dashboard'),
    path('api/ai_chat/', views.ai_chat_view, name='ai_chat'),
    path('api/ai_chat_public/', views.ai_chat_public_view, name='ai_chat_public'),
    path('api/save_push_subscription/', views.save_push_subscription, name='save_push_subscription'),
    
    # The root path still points to the view that redirects users
    path('', views.home_view, name='home'), 
]