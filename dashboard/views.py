from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
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
You are AquaSavvy AI Assistant for water management systems. 

RESPONSE STYLE:
- Be BRIEF and PRECISE (max 2-3 sentences)
- Answer directly to the question asked
- Use bullet points for multiple items
- No lengthy explanations unless specifically requested

SYSTEM CAPABILITIES:
- Tank level monitoring (Overhead/Underground)
- Pump control and automation
- 4 timeslots for scheduling
- Real-time WebSocket updates
- Dashboard with charts and controls

COMMON QUERIES:
- Tank levels: "Tank at X% - Normal/Low/High"
- Pump status: "Pump ON/OFF - Running X minutes"
- Automation: "Rule active/inactive - Next run at X"
- Issues: "Check [specific component] - [brief solution]"

SUPPORT: contact:vision072025@gmail.com | WhatsApp: +254 702 715070

Keep responses concise and actionable.
"""

# Custom Login/Logout Views
class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

class CustomLogoutView(LogoutView):
    next_page = 'public_home'

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'password_change.html'
    success_url = '/devices/'
    
    def form_valid(self, form):
        messages.success(self.request, 'Your password has been changed successfully!')
        return super().form_valid(form)

def home_view(request):
    return render(request, 'public_home.html')

@login_required
def device_list_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get user's devices and unassigned devices
    user_devices = request.user.device_set.all()
    unassigned_devices = Device.objects.filter(owner__isnull=True)
    
    return render(request, 'device_list.html', {
        'devices': user_devices,
        'unassigned_devices': unassigned_devices
    })

@login_required
def claim_device_view(request, device_id):
    """Allow user to claim an unassigned device"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    device = get_object_or_404(Device, device_id=device_id, owner__isnull=True)
    device.owner = request.user
    device.name = device.name or f"{request.user.username}'s Device"
    device.save()
    
    print(f"✅ Device '{device_id}' claimed by user '{request.user.username}'")
    return redirect('device_list')

@login_required
def dashboard_view(request, device_id):
    # Allow access to devices owned by user OR unassigned devices
    try:
        device = get_object_or_404(Device, device_id=device_id)
        if device.owner and device.owner != request.user:
            return redirect('login')  # Redirect to login if trying to access someone else's device
    except:
        return redirect('login')
    
    # Get latest reading
    last_reading = device.readings.last()
    
    # Get automation rules
    automation_rules = device.rules.all()
    
    # Debug logging
    print(f"🔍 Dashboard view for device: {device_id}")
    print(f"📊 Latest reading: {last_reading}")
    print(f"📈 Total readings: {device.readings.count()}")
    
    return render(request, 'dashboard.html', {
        'device': device,
        'last_reading': last_reading,
        'automation_rules': automation_rules
    })

@csrf_exempt
@require_http_methods(["POST"])
def ai_chat_view(request):
    """Handle AI chat requests with streaming support"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        stream = data.get('stream', False)
        
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
            'gemini-2.0-flash-exp',  # Using latest model for better performance
            system_instruction=DEVICE_INFO
        )
        
        if stream:
            # For streaming responses using the correct API
            response = model.generate_content(
                user_message,
                stream=True
            )
            
            # Create streaming response
            def generate_stream():
                full_response = ""
                for chunk in response:
                    if hasattr(chunk, 'text') and chunk.text:
                        full_response += chunk.text
                        yield f"data: {json.dumps({'chunk': chunk.text, 'status': 'streaming'})}\n\n"
                
                # Send final complete response
                yield f"data: {json.dumps({'reply': full_response, 'status': 'complete'})}\n\n"
                yield "data: [DONE]\n\n"
            
            from django.http import StreamingHttpResponse
            return StreamingHttpResponse(
                generate_stream(),
                content_type='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                }
            )
        else:
            # For non-streaming responses (fallback)
        response = model.generate_content(user_message)
        
        return JsonResponse({
            'reply': response.text,
            'status': 'success'
        })
        
    except Exception as e:
        # Provide a helpful fallback response
        fallback_response = f"I'm having trouble processing your request. Error: {str(e)}. Please try again or contact support at contact:vision072025@gmail.com"
        
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
        
        # Get device shadow from AWS IoT (optional - don't fail if not available)
        try:
        shadow_data = aws_iot_manager.get_device_shadow(device_id)
        except Exception as e:
            print(f"⚠️ Could not get device shadow for {device_id}: {e}")
            shadow_data = None
        
        readings_data = []
        for reading in recent_readings:
            readings_data.append({
                'id': reading.id,
                'timestamp': reading.timestamp.isoformat(),
                'system_data': reading.system_data
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
                'pump_present': device.pump_present,
                'overload_current_amps': device.overload_current_amps,
                'dry_run_current_amps': device.dry_run_current_amps,
                'tank_names': device.get_tank_names(),
                'tank_1_reading_id': device.tank_1_reading_id,
                'tank_1_name': device.tank_1_name,
                'tank_2_reading_id': device.tank_2_reading_id,
                'tank_2_name': device.tank_2_name,
                'tank_3_reading_id': device.tank_3_reading_id,
                'tank_3_name': device.tank_3_name,
                'tank_4_reading_id': device.tank_4_reading_id,
                'tank_4_name': device.tank_4_name
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

@login_required
def device_data_api(request, device_id):
    """API endpoint for live device data updates"""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
    
    try:
        device = get_object_or_404(Device, device_id=device_id)
        
        # Check if user owns this device or is superuser
        if device.owner != request.user and not request.user.is_superuser:
            return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
        
        # Get latest reading
        latest_reading = WaterReading.objects.filter(device=device).order_by('-timestamp').first()
        
        if not latest_reading:
            return JsonResponse({
                'status': 'success',
                'tank_data': [],
                'pump_status': False,
                'pump_current_amps': 0.0,
                'timestamp': None
            })
        
        # Extract data from system_data JSONField
        system_data = latest_reading.system_data or {}
        
        # Create tank_data from system_data
        tank_data = []
        for key, value in system_data.items():
            if key.endswith('_level'):
                tank_name = key.replace('_level', '').replace('_', ' ').title()
                tank_data.append({
                    'name': tank_name,
                    'level': value,
                    'capacity': '1000L'  # Default capacity
                })
        
        return JsonResponse({
            'status': 'success',
            'tank_data': tank_data,
            'pump_status': system_data.get('pump_status', False),
            'pump_current_amps': system_data.get('pump_current', 0.0),
            'timestamp': latest_reading.timestamp.isoformat()
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def notification_preference_api(request):
    """API endpoint for push notification preferences"""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            enabled = data.get('enabled', False)
            device_id = data.get('device_id')
            
            if device_id:
                device = get_object_or_404(Device, device_id=device_id)
                if device.owner != request.user and not request.user.is_superuser:
                    return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
                
                # Update or create notification preference
                from .models import Profile
                profile, created = Profile.objects.get_or_create(user=request.user)
                profile.push_notifications = enabled
                profile.save()
                
                return JsonResponse({
                    'status': 'success',
                    'message': f'Notifications {"enabled" if enabled else "disabled"} for device {device_id}'
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'Device ID required'}, status=400)
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)