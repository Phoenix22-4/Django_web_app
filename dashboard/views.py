from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import google.generativeai as genai
import os

# Configure Gemini AI
genai.configure(api_key=os.getenv('GEMINI_API_KEY', 'your-api-key-here'))

# AquaSavvy device information for AI training
DEVICE_INFO = """
AquaSavvy Water Management System:

System Overview:
- Smart water monitoring and control system
- Real-time tank level monitoring
- Automated pump control
- WebSocket connectivity for live updates
- Mobile-responsive dashboard

Device Components:
1. Water Tanks (Overhead/Underground)
   - Level sensors for real-time monitoring
   - Visual indicators for tank status
   - Support for multiple tanks (up to 4)

2. Pump System
   - Automated pump control
   - Real-time status monitoring
   - Current and power usage tracking
   - Visual pump icon with animation

3. Automation System
   - 4 configurable timeslots
   - Rule-based automation
   - Tank level thresholds
   - Time-based scheduling

4. Dashboard Features
   - Real-time charts (pump runtime, power usage)
   - Tank level visualization
   - Connection status indicators
   - Automation rule management

Troubleshooting Guide:
- Connection Issues: Check WebSocket status, verify device connectivity
- Pump Problems: Check power supply, verify pump status indicators
- Tank Monitoring: Ensure sensors are clean and properly connected
- Automation: Verify rule configuration and time settings

Maintenance Tips:
- Regular sensor cleaning
- Pump maintenance checks
- System updates and monitoring
- Backup power considerations

Support Information:
- Email: contact:vision072025@gmail.com
- WhatsApp: +254 702 715070
- System Documentation: Available in dashboard
"""

# Custom Login/Logout Views
class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

class CustomLogoutView(LogoutView):
    next_page = 'public_home'

def home_view(request):
    return render(request, 'public_home.html')

@login_required
def device_list_view(request):
    devices = request.user.devices.all()
    return render(request, 'device_list.html', {'devices': devices})

@login_required
def dashboard_view(request, device_id):
    device = get_object_or_404(request.user.devices, device_id=device_id)
    
    # Get latest reading
    last_reading = device.readings.last()
    
    # Get automation rules
    automation_rules = device.automation_rules.all()
    
    return render(request, 'dashboard.html', {
        'device': device,
        'last_reading': last_reading,
        'automation_rules': automation_rules
    })

@csrf_exempt
@require_http_methods(["POST"])
def ai_chat_view(request):
    """Handle AI chat requests"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        if not user_message:
            return JsonResponse({'error': 'No message provided'}, status=400)
        
        # Initialize Gemini model with device information
        model = genai.GenerativeModel(
            'gemini-1.5-pro',
            system_instruction=DEVICE_INFO
        )
        
        # Generate response
        response = model.generate_content(user_message)
        
        return JsonResponse({
            'reply': response.text,
            'status': 'success'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'AI service error: {str(e)}',
            'status': 'error'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def save_rule_view(request):
    """Save automation rule"""
    try:
        data = json.loads(request.body)
        
        # Implementation for saving automation rules
        # This would integrate with your AutomationRule model
        
        return JsonResponse({
            'status': 'success',
            'message': 'Rule saved successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error saving rule: {str(e)}',
            'status': 'error'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def delete_rule_view(request):
    """Delete automation rule"""
    try:
        data = json.loads(request.body)
        
        # Implementation for deleting automation rules
        
        return JsonResponse({
            'status': 'success',
            'message': 'Rule deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error deleting rule: {str(e)}',
            'status': 'error'
        }, status=500)