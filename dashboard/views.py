from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import google.generativeai as genai
import os
from datetime import datetime
from .aws_iot_integration import aws_iot_manager
from .models import Device, WaterReading, AutomationRule
from .push_notifications import push_notification_service

# Configure Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("WARNING: GEMINI_API_KEY not found in environment variables")

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
    devices = request.user.device_set.all()
    return render(request, 'device_list.html', {'devices': devices})

@login_required
def dashboard_view(request, device_id):
    device = get_object_or_404(request.user.device_set, device_id=device_id)
    
    # Get latest reading
    last_reading = device.readings.last()
    
    # Get automation rules
    automation_rules = device.rules.all()
    
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
        
        # Check if Gemini API key is available
        if not GEMINI_API_KEY:
            return JsonResponse({
                'reply': 'AI chat is currently unavailable. Please contact support at contact:vision072025@gmail.com or WhatsApp: +254 702 715070',
                'status': 'error',
                'error_type': 'api_key_missing'
            })
        
        # Initialize Gemini model with device information
        model = genai.GenerativeModel(
            'gemini-2.5-flash',  # Using Gemini 1.5 Flash for speed and performance
            system_instruction=DEVICE_INFO
        )
        
        # Generate response
        response = model.generate_content(user_message)
        
        return JsonResponse({
            'reply': response.text,
            'status': 'success'
        })
        
    except Exception as e:
        # Provide a helpful fallback response
        fallback_response = f"I'm sorry, I'm having trouble processing your request right now. Error: {str(e)}. Please try again or contact support at contact:vision072025@gmail.com"
        
        return JsonResponse({
            'reply': fallback_response,
            'status': 'error',
            'error': str(e)
        })

@csrf_exempt
@require_http_methods(["POST"])
def save_rule_view(request):
    """Save automation rule"""
    try:
        data = json.loads(request.body)
        
        device_id = data.get('device_id')
        rule_id = data.get('rule_id')  # For updates
        name = data.get('name', 'My Rule')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        monitor_tank_name = data.get('monitor_tank_name', 'Overhead')
        min_level = data.get('min_level', 20)
        max_level = data.get('max_level', 95)
        enabled = data.get('enabled', True)
        
        if not device_id:
            return JsonResponse({'error': 'Device ID required'}, status=400)
        
        # Check if user owns the device
        device = get_object_or_404(Device, device_id=device_id, owner=request.user)
        
        if rule_id:
            # Update existing rule
            rule = get_object_or_404(AutomationRule, id=rule_id, device=device)
            rule.name = name
            rule.start_time = start_time
            rule.end_time = end_time
            rule.monitor_tank_name = monitor_tank_name
            rule.min_level = min_level
            rule.max_level = max_level
            rule.enabled = enabled
            rule.save()
            action = 'updated'
        else:
            # Create new rule
            rule = AutomationRule.objects.create(
                device=device,
                name=name,
                start_time=start_time,
                end_time=end_time,
                monitor_tank_name=monitor_tank_name,
                min_level=min_level,
                max_level=max_level,
                enabled=enabled
            )
            action = 'created'
        
        return JsonResponse({
            'status': 'success',
            'message': f'Rule {action} successfully',
            'rule_id': rule.id
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
        
        rule_id = data.get('rule_id')
        device_id = data.get('device_id')
        
        if not rule_id or not device_id:
            return JsonResponse({'error': 'Rule ID and Device ID required'}, status=400)
        
        # Check if user owns the device
        device = get_object_or_404(Device, device_id=device_id, owner=request.user)
        
        # Delete the rule
        rule = get_object_or_404(AutomationRule, id=rule_id, device=device)
        rule.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Rule deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error deleting rule: {str(e)}',
            'status': 'error'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def aws_iot_data_endpoint(request):
    """Receive device data from AWS IoT"""
    try:
        data = json.loads(request.body)
        device_id = data.get('device_id')
        
        if not device_id:
            return JsonResponse({'error': 'Device ID required'}, status=400)
        
        # Process the device data
        reading = aws_iot_manager.process_device_data(device_id, data)
        
        if reading:
            return JsonResponse({
                'status': 'success',
                'message': 'Data processed successfully',
                'reading_id': reading.id
            })
        else:
            return JsonResponse({
                'error': 'Failed to process device data',
                'status': 'error'
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'error': f'Error processing IoT data: {str(e)}',
            'status': 'error'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def pump_control_view(request):
    """Manual pump control"""
    try:
        data = json.loads(request.body)
        device_id = data.get('device_id')
        pump_on = data.get('pump_on', False)
        
        if not device_id:
            return JsonResponse({'error': 'Device ID required'}, status=400)
        
        # Check if user owns the device
        device = get_object_or_404(Device, device_id=device_id, owner=request.user)
        
        # Send command to device
        success = aws_iot_manager.send_manual_command(device_id, 'pump_control', pump_on)
        
        if success:
            return JsonResponse({
                'status': 'success',
                'message': f'Pump {"turned ON" if pump_on else "turned OFF"} successfully'
            })
        else:
            return JsonResponse({
                'error': 'Failed to send command to device',
                'status': 'error'
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'error': f'Error controlling pump: {str(e)}',
            'status': 'error'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def device_command_view(request):
    """Send general command to device"""
    try:
        data = json.loads(request.body)
        device_id = data.get('device_id')
        command = data.get('command')
        value = data.get('value')
        
        if not device_id or not command:
            return JsonResponse({'error': 'Device ID and command required'}, status=400)
        
        # Check if user owns the device
        device = get_object_or_404(Device, device_id=device_id, owner=request.user)
        
        # Send command to device
        success = aws_iot_manager.send_manual_command(device_id, command, value)
        
        if success:
            return JsonResponse({
                'status': 'success',
                'message': f'Command "{command}" sent successfully'
            })
        else:
            return JsonResponse({
                'error': 'Failed to send command to device',
                'status': 'error'
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'error': f'Error sending command: {str(e)}',
            'status': 'error'
        }, status=500)

@login_required
def device_data_view(request, device_id):
    """Get device data and readings"""
    try:
        device = get_object_or_404(Device, device_id=device_id, owner=request.user)
        
        # Get recent readings
        recent_readings = device.readings.order_by('-timestamp')[:10]
        
        # Get automation rules
        automation_rules = device.rules.all()
        
        # Get device shadow from AWS IoT
        shadow_data = aws_iot_manager.get_device_shadow(device_id)
        
        readings_data = []
        for reading in recent_readings:
            readings_data.append({
                'id': reading.id,
                'timestamp': reading.timestamp.isoformat(),
                'pump_status': reading.pump_status,
                'pump_current_amps': reading.pump_current_amps,
                'tank_data': reading.tank_data
            })
        
        rules_data = []
        for rule in automation_rules:
            rules_data.append({
                'id': rule.id,
                'name': rule.name,
                'start_time': rule.start_time.isoformat(),
                'end_time': rule.end_time.isoformat(),
                'monitor_tank_name': rule.monitor_tank_name,
                'min_level': rule.min_level,
                'max_level': rule.max_level,
                'enabled': rule.enabled
            })
        
        return JsonResponse({
            'status': 'success',
            'device': {
                'device_id': device.device_id,
                'name': device.name,
                'tank_capacity_liters': device.tank_capacity_liters,
                'pump_present': device.pump_present
            },
            'readings': readings_data,
            'automation_rules': rules_data,
            'shadow_data': shadow_data
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error getting device data: {str(e)}',
            'status': 'error'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def register_fcm_token(request):
    """Register FCM token for push notifications"""
    try:
        data = json.loads(request.body)
        fcm_token = data.get('fcm_token')
        
        if not fcm_token:
            return JsonResponse({'error': 'FCM token required'}, status=400)
        
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        # Update user's FCM token
        profile = request.user.get_profile()
        profile.fcm_token = fcm_token
        profile.save()
        
        # Send welcome notification
        push_notification_service.send_welcome_notification(request.user)
        
        return JsonResponse({
            'status': 'success',
            'message': 'FCM token registered successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error registering FCM token: {str(e)}',
            'status': 'error'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def test_notification(request):
    """Send test notification"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        success = push_notification_service.send_notification_to_user(
            request.user,
            "Test Notification",
            "This is a test notification from AquaSavvy!",
            {"type": "test", "timestamp": datetime.now().isoformat()}
        )
        
        if success:
            return JsonResponse({
                'status': 'success',
                'message': 'Test notification sent successfully'
            })
        else:
            return JsonResponse({
                'error': 'Failed to send test notification',
                'status': 'error'
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'error': f'Error sending test notification: {str(e)}',
            'status': 'error'
        }, status=500)