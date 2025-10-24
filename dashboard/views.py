from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
import json
import google.generativeai as genai
import os
from datetime import datetime
from django.utils import timezone
from .security_decorators import (
    secure_api_view, validate_json_input, device_ownership_required,
    rate_limit, sanitize_input
)
import logging

logger = logging.getLogger(__name__)

# Import with error handling for local development
try:
    from .aws_iot_integration import aws_iot_manager
except ImportError:
    print("WARNING: AWS IoT integration not available")
    aws_iot_manager = None

from .models import Device, WaterReading, AutomationRule

try:
    from .push_notifications import push_notification_service
except ImportError:
    print("WARNING: Push notifications not available")
    push_notification_service = None

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

# CSRF Failure View
def csrf_failure_view(request, reason=""):
    """Custom CSRF failure view with security logging."""
    logger.warning(f"CSRF failure for IP {get_client_ip(request)}: {reason}")
    return HttpResponseForbidden(
        '<h1>403 Forbidden</h1><p>CSRF verification failed. Please refresh the page and try again.</p>'
    )

def get_client_ip(request):
    """Get client IP address from request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# Custom Login/Logout Views with Enhanced Security
class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True
    
    @method_decorator(rate_limit(max_requests=5, window_seconds=300))  # 5 attempts per 5 minutes
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Log successful login
        print(f"🔐 User '{form.get_user().username}' logged in successfully from IP {get_client_ip(self.request)}")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Log failed login attempt
        username = form.cleaned_data.get('username', 'unknown')
        print(f"❌ Failed login attempt for user '{username}' from IP {get_client_ip(self.request)}")
        return super().form_invalid(form)

class CustomLogoutView(LogoutView):
    next_page = 'public_home'
    
    def dispatch(self, request, *args, **kwargs):
        # Log the logout action
        if request.user.is_authenticated:
            print(f"🔒 User '{request.user.username}' logged out")
        return super().dispatch(request, *args, **kwargs)

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'password_change.html'
    success_url = '/devices/'
    
    def form_valid(self, form):
        messages.success(self.request, 'Your password has been changed successfully!')
        
        # Send password change notification
        try:
            # Store password change notification in session for JavaScript to pick up
            self.request.session['password_change_notification'] = {
                'title': '🔐 AquaGuard Alert - Password Changed',
                'message': f'Your system password was changed by {self.request.user.username} at {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}.',
                'timestamp': timezone.now().isoformat()
            }
        except Exception as e:
            print(f"Error storing password change notification: {e}")
        
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
    
    # Check for password change notification
    password_change_notification = None
    if 'password_change_notification' in request.session:
        password_change_notification = request.session.pop('password_change_notification')
    
    context = {
        'devices': user_devices,
        'unassigned_devices': unassigned_devices,
        'password_change_notification': password_change_notification
    }
    
    return render(request, 'device_list.html', context)

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
    
    # Get usage analytics data (filtered based on device type)
    if device.pump_present:
        # Full analytics for devices with pumps
        usage_data = device.readings.all().order_by('-timestamp')[:100]
    else:
        # Filtered analytics for monitoring-only devices
        usage_data = device.readings.all().order_by('-timestamp')[:100]
    
    # Debug logging
    print(f"🔍 Dashboard view for device: {device_id}")
    print(f"📊 Latest reading: {last_reading}")
    print(f"📈 Total readings: {device.readings.count()}")
    print(f"🔧 Device has pump: {device.pump_present}")
    
    return render(request, 'dashboard.html', {
        'device': device,
        'last_reading': last_reading,
        'automation_rules': automation_rules,
        'usage_data': usage_data,
        'has_pump': device.pump_present,
        'is_monitoring_only': not device.pump_present,
    })

@secure_api_view(require_auth=False, allowed_methods=['POST'], rate_limit_requests=20)
@validate_json_input(required_fields=['message'], optional_fields={'stream': 'boolean'})
def ai_chat_view(request):
    """Handle AI chat requests with streaming support"""
    try:
        data = request.validated_data
        user_message = sanitize_input(data.get('message', ''))
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

@secure_api_view(require_auth=True, allowed_methods=['POST'], rate_limit_requests=10)
@validate_json_input(required_fields=['device_id'], optional_fields={
    'rule_id': 'integer', 'name': 'string', 'start_time': 'string', 
    'end_time': 'string', 'monitor_tank_name': 'string', 
    'min_level': 'integer', 'max_level': 'integer', 'enabled': 'boolean'
})
@device_ownership_required
def save_rule_view(request):
    """Save automation rule"""
    try:
        data = request.validated_data
        device = request.device  # Already validated by device_ownership_required
        
        rule_id = data.get('rule_id')  # For updates
        name = sanitize_input(data.get('name', 'My Rule'))
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        monitor_tank_name = sanitize_input(data.get('monitor_tank_name', 'Overhead'))
        min_level = data.get('min_level', 20)
        max_level = data.get('max_level', 95)
        enabled = data.get('enabled', True)
        
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

@secure_api_view(require_auth=True, allowed_methods=['POST'], rate_limit_requests=10)
@validate_json_input(required_fields=['rule_id', 'device_id'])
@device_ownership_required
def delete_rule_view(request):
    """Delete automation rule"""
    try:
        data = request.validated_data
        device = request.device  # Already validated by device_ownership_required
        
        rule_id = data.get('rule_id')
        
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

@secure_api_view(require_auth=False, allowed_methods=['POST'], rate_limit_requests=100)
@validate_json_input(required_fields=['device_id'])
def aws_iot_data_endpoint(request):
    """Receive device data from AWS IoT"""
    try:
        data = request.validated_data
        device_id = sanitize_input(data.get('device_id'))
        
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

@secure_api_view(require_auth=True, allowed_methods=['POST'], rate_limit_requests=20)
@validate_json_input(required_fields=['device_id'], optional_fields={'pump_on': 'boolean'})
@device_ownership_required
def pump_control_view(request):
    """Manual pump control"""
    try:
        data = request.validated_data
        device = request.device  # Already validated by device_ownership_required
        pump_on = data.get('pump_on', False)
        
        # Send command to device
        success = aws_iot_manager.send_manual_command(device.device_id, 'pump_control', pump_on)
        
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

@secure_api_view(require_auth=True, allowed_methods=['POST'], rate_limit_requests=20)
@validate_json_input(required_fields=['device_id', 'command'], optional_fields={'value': 'string'})
@device_ownership_required
def device_command_view(request):
    """Send general command to device"""
    try:
        data = request.validated_data
        device = request.device  # Already validated by device_ownership_required
        command = sanitize_input(data.get('command'))
        value = sanitize_input(data.get('value', ''))
        
        # Send command to device
        success = aws_iot_manager.send_manual_command(device.device_id, command, value)
        
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

@secure_api_view(require_auth=True, allowed_methods=['POST'], rate_limit_requests=20)
@validate_json_input(required_fields=['device_id', 'solenoid_index'], optional_fields={
    'solenoid_name': 'string', 'solenoid_on': 'boolean'
})
@device_ownership_required
def solenoid_control_view(request):
    """Manual solenoid valve control"""
    try:
        data = request.validated_data
        device = request.device  # Already validated by device_ownership_required
        solenoid_index = data.get('solenoid_index')
        solenoid_name = sanitize_input(data.get('solenoid_name', ''))
        solenoid_on = data.get('solenoid_on', False)
        
        # Send command to device
        command_data = {
            'solenoid_index': solenoid_index,
            'solenoid_name': solenoid_name,
            'solenoid_on': solenoid_on
        }
        
        success = aws_iot_manager.send_manual_command(device.device_id, 'solenoid_control', command_data)
        
        if success:
            return JsonResponse({
                'status': 'success',
                'message': f'Solenoid {solenoid_index} (${solenoid_name}) {"turned ON" if solenoid_on else "turned OFF"} successfully'
            })
        else:
            return JsonResponse({
                'error': 'Failed to send solenoid command to device',
                'status': 'error'
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'error': f'Error controlling solenoid: {str(e)}',
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
                'tank_4_name': device.tank_4_name,
                'solenoid_names': device.get_solenoid_names(),
                'solenoid_1_reading_id': device.solenoid_1_reading_id,
                'solenoid_1_name': device.solenoid_1_name,
                'solenoid_2_reading_id': device.solenoid_2_reading_id,
                'solenoid_2_name': device.solenoid_2_name,
                'solenoid_3_reading_id': device.solenoid_3_reading_id,
                'solenoid_3_name': device.solenoid_3_name,
                'solenoid_4_reading_id': device.solenoid_4_reading_id,
                'solenoid_4_name': device.solenoid_4_name
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

@secure_api_view(require_auth=True, allowed_methods=['POST'], rate_limit_requests=10)
@validate_json_input(required_fields={'token': 'string'})
def save_fcm_token(request):
    """Save FCM token from client-side (matches client endpoint)"""
    try:
        data = request.validated_data
        fcm_token = sanitize_input(data.get('token', ''))
        
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        if not fcm_token:
            return JsonResponse({'error': 'FCM token is required'}, status=400)
        
        # Store token in FCMToken model for multiple devices per user
        from .models import FCMToken
        from django.utils import timezone
        
        # Get user agent for device identification
        user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')
        device_type = 'web'  # Default for web browsers
        
        # Create or update FCM token
        fcm_token_obj, created = FCMToken.objects.get_or_create(
            user=request.user,
            token=fcm_token,
            defaults={
                'device_type': device_type,
                'user_agent': user_agent,
                'is_active': True,
                'last_used': timezone.now()
            }
        )
        
        if not created:
            # Update existing token
            fcm_token_obj.is_active = True
            fcm_token_obj.last_used = timezone.now()
            fcm_token_obj.user_agent = user_agent
            fcm_token_obj.save()
        
        # Also update Profile for backward compatibility
        from .models import Profile
        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile.fcm_token = fcm_token
        profile.push_notifications_enabled = True
        profile.save()
        
        # Log with special user number for easy identification
        special_number = getattr(profile, 'special_user_number', 'N/A')
        print(f"📱 FCM TOKEN REGISTRATION: {'NEW' if created else 'UPDATED'} token for user '{request.user.username}' (ID: {request.user.id}, Special #: {special_number})")
        print(f"📱 FCM TOKEN DETAILS: Token ID: {fcm_token_obj.id}, Device Type: {fcm_token_obj.device_type}, Active: {fcm_token_obj.is_active}")
        print(f"📱 FCM TOKEN PREVIEW: {fcm_token[:20]}...{fcm_token[-10:]}")
        
        return JsonResponse({
            'status': 'success',
            'message': 'FCM token saved successfully',
            'token_id': fcm_token_obj.id,
            'special_user_number': special_number
        })
        
    except Exception as e:
        print(f"❌ Error in save_fcm_token: {e}")
        return JsonResponse({'error': 'Failed to save FCM token'}, status=500)

@secure_api_view(require_auth=True, allowed_methods=['POST'], rate_limit_requests=10)
@validate_json_input(optional_fields={'fcm_token': 'string', 'enabled': 'boolean'})
def register_fcm_token(request):
    """Register FCM token for push notifications"""
    try:
        data = request.validated_data
        fcm_token = sanitize_input(data.get('fcm_token', ''))
        enabled = data.get('enabled', False)
        
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        # Update user's notification preference
        try:
            from .models import Profile
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.fcm_token = fcm_token or 'browser_notification'
            profile.push_notifications_enabled = enabled
            profile.save()
            
            print(f"📱 Notification preference updated for user '{request.user.username}': {enabled}")
            
            return JsonResponse({
                'status': 'success',
                'message': f'Notification preference {"enabled" if enabled else "disabled"} successfully'
            })
        except Exception as e:
            print(f"❌ Error updating notification preference: {e}")
            return JsonResponse({
                'error': f'Error updating notification preference: {str(e)}',
                'status': 'error'
            }, status=500)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error registering FCM token: {str(e)}',
            'status': 'error'
        }, status=500)

@secure_api_view(require_auth=True, allowed_methods=['POST'], rate_limit_requests=5)
def test_notification(request):
    """Send test notification"""
    try:
        
        # For browser notifications, we'll just return success
        # The actual notification will be shown by the JavaScript
        print(f"🔔 Test notification requested by user '{request.user.username}'")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Test notification sent successfully'
        })
            
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
        
        # Create solenoid_data from system_data
        solenoid_data = []
        for key, value in system_data.items():
            if key.endswith('_solenoid'):
                solenoid_name = key.replace('_solenoid', '').replace('_', ' ').title()
                solenoid_data.append({
                    'name': solenoid_name,
                    'isOn': bool(value),
                    'index': len(solenoid_data) + 1
                })
        
        return JsonResponse({
            'status': 'success',
            'tank_data': tank_data,
            'solenoid_data': solenoid_data,
            'pump_status': system_data.get('pump_status', False),
            'pump_current_amps': system_data.get('pump_current', 0.0),
            'water_usage': system_data.get('water_usage', 0.0),
            'pump_runtime': system_data.get('pump_runtime', 0.0),
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
                profile.push_notifications_enabled = enabled
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


def firebase_service_worker(request):
    """Serve Firebase service worker with dynamic configuration"""
    from django.conf import settings
    from django.http import HttpResponse
    
    # Get Firebase configuration from environment variables
    firebase_config = {
        'apiKey': settings.FIREBASE_API_KEY,
        'authDomain': f"{settings.FIREBASE_PROJECT_ID}.firebaseapp.com",
        'projectId': settings.FIREBASE_PROJECT_ID,
        'storageBucket': f"{settings.FIREBASE_PROJECT_ID}.appspot.com",
        'messagingSenderId': settings.FIREBASE_MESSAGING_SENDER_ID,
        'appId': settings.FIREBASE_APP_ID,
    }
    
    # Generate the service worker content
    service_worker_content = f"""// Firebase Service Worker for AquaSavvy
try {{
    importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-app-compat.js');
    importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-messaging-compat.js');

    // Initialize Firebase with secure configuration
    firebase.initializeApp({{
        apiKey: "{firebase_config['apiKey']}",
        authDomain: "{firebase_config['authDomain']}",
        projectId: "{firebase_config['projectId']}",
        storageBucket: "{firebase_config['storageBucket']}",
        messagingSenderId: "{firebase_config['messagingSenderId']}",
        appId: "{firebase_config['appId']}"
    }});

    // Initialize Firebase Messaging
    const messaging = firebase.messaging();
}} catch (error) {{
    console.log('Firebase messaging not available in service worker context:', error);
}}

// Handle background messages
try {{
    if (typeof messaging !== 'undefined') {{
        messaging.onBackgroundMessage(function(payload) {{
            console.log('[firebase-messaging-sw.js] Received background message ', payload);
            
            const notificationTitle = payload.notification.title || 'AquaSavvy Notification';
            const notificationOptions = {{
                body: payload.notification.body || 'You have a new notification',
                icon: '/static/images/chat-icon.png',
                badge: '/static/images/chat-icon.png',
                tag: 'aquasavvy-notification',
                requireInteraction: true,
                actions: [
                    {{
                        action: 'view',
                        title: 'View Dashboard'
                    }},
                    {{
                        action: 'dismiss',
                        title: 'Dismiss'
                    }}
                ]
            }};

            self.registration.showNotification(notificationTitle, notificationOptions);
        }});
    }}
}} catch (error) {{
    console.log('Firebase messaging background handler not available:', error);
}}

// Handle notification clicks
self.addEventListener('notificationclick', function(event) {{
    console.log('[firebase-messaging-sw.js] Notification click received.');
    
    event.notification.close();
    
    if (event.action === 'view') {{
        // Open the dashboard
        event.waitUntil(
            clients.openWindow('/devices/')
        );
    }} else if (event.action === 'dismiss') {{
        // Just close the notification
        return;
    }} else {{
        // Default action - open the app
        event.waitUntil(
            clients.openWindow('/')
        );
    }}
}});
"""
    
    return HttpResponse(service_worker_content, content_type='application/javascript')