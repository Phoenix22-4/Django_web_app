# dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('devices/', views.device_list_view, name='device_list'),
    path('dashboard/<str:device_id>/', views.dashboard_view, name='dashboard'),
    
    # --- CHANGE: The root path now points to the new home_view ---
    path('', views.home_view, name='home'), 
]