# dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('change-password/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('devices/', views.device_list_view, name='device_list'),
    path('claim-device/<str:device_id>/', views.claim_device_view, name='claim_device'),
    path('dashboard/<str:device_id>/', views.dashboard_view, name='dashboard'),
    
    # --- CHANGE: The root path now points to the new public home_view ---
    path('', views.home_view, name='public_home'), 
    path('home/', views.home_view, name='public_home_alias'), # Alias for 'home'

    # --- NEW: API URLs FOR CHAT AND AUTOMATION ---
    path('api/ai_chat/', views.ai_chat_view, name='ai_chat'),
    path('api/save_rule/', views.save_rule_view, name='save_rule'),
    path('api/delete_rule/', views.delete_rule_view, name='delete_rule'),
    
    # --- NEW: AWS IOT AND DEVICE CONTROL URLs ---
    path('api/iot_data/', views.aws_iot_data_endpoint, name='aws_iot_data'),
    path('api/pump_control/', views.pump_control_view, name='pump_control'),
    path('api/device_command/', views.device_command_view, name='device_command'),
    path('api/device_data/<str:device_id>/', views.device_data_view, name='device_data'),
    
    # --- NEW: PUSH NOTIFICATION URLs ---
    path('api/register_fcm_token/', views.register_fcm_token, name='register_fcm_token'),
    path('api/test_notification/', views.test_notification, name='test_notification'),
    
    # --- NEW: LIVE DATA AND NOTIFICATION PREFERENCE URLs ---
    path('api/device_data/<str:device_id>/', views.device_data_api, name='device_data_api'),
    path('api/notification-preference/', views.notification_preference_api, name='notification_preference_api'),
]