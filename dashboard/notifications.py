"""
Push Notifications using Firebase Admin SDK (V1 API)
Sends alerts for critical water system events with cooldown logic.
"""
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from .models import Device, WaterReading
import json
import os

# Firebase Admin SDK initialization
try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    
    # Check if already initialized
    if not firebase_admin._apps:
        # Try to get credentials from environment variable (JSON string)
        firebase_creds_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')
        
        if firebase_creds_json:
            # Parse JSON string from environment variable
            cred_dict = json.loads(firebase_creds_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase Admin SDK initialized from environment variable")
        elif os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
            # Fallback: Try to load from file
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase Admin SDK initialized from file")
        else:
            print("⚠️ Firebase credentials not found. Push notifications will be disabled.")
            firebase_admin = None
except ImportError:
    print("⚠️ firebase-admin not installed. Push notifications will be disabled.")
    firebase_admin = None
except Exception as e:
    print(f"⚠️ Firebase initialization error: {e}")
    firebase_admin = None


ALERT_COOLDOWN_MINUTES = 60


def _cooldown_ok(device: Device, alert_type: str) -> bool:
    """Check if cooldown period has passed for this alert type."""
    if not device.last_alert_type or not device.last_alert_sent_at:
        return True
    if device.last_alert_type != alert_type:
        return True
    return device.last_alert_sent_at <= timezone.now() - timedelta(minutes=ALERT_COOLDOWN_MINUTES)


def _mark_alert_sent(device: Device, alert_type: str) -> None:
    """Update device with alert timestamp to prevent spam."""
    device.last_alert_type = alert_type
    device.last_alert_sent_at = timezone.now()
    device.save(update_fields=['last_alert_type', 'last_alert_sent_at'])


def _send_fcm_notification(device: Device, title: str, body: str) -> None:
    """
    Send push notification using Firebase Admin SDK (V1 API).
    Sends to all FCM tokens registered for the device owner.
    """
    if not device.owner:
        print(f"⚠️ Device {device.device_id} has no owner. Cannot send notification.")
        return
    
    if not firebase_admin:
        print(f"⚠️ Firebase Admin SDK not initialized. Skipping notification for {device.device_id}")
        return
    
    try:
        # Get FCM tokens for this user from database
        # You'll need to store FCM tokens in your database (see views.py)
        from .models import FCMToken
        tokens = FCMToken.objects.filter(user=device.owner, is_active=True).values_list('token', flat=True)
        
        if not tokens:
            print(f"⚠️ No FCM tokens found for user {device.owner.username}")
            return
        
        # Create the message
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
                # icon='/static/img/aquasavvy_icon.png'  # Optional: Add your icon
            ),
            data={
                'device_id': device.device_id,
                'device_name': device.name or device.device_id,
                'alert_type': device.last_alert_type or 'UNKNOWN',
                'click_action': f'/dashboard/{device.device_id}/'
            },
            tokens=list(tokens)
        )
        
        # Send the message
        response = messaging.send_multicast(message)
        
        # Log results
        print(f"✅ Push notification sent: {response.success_count} successful, {response.failure_count} failed")
        
        # Handle failed tokens (cleanup invalid tokens)
        if response.failure_count > 0:
            for idx, resp in enumerate(response.responses):
                if not resp.success:
                    failed_token = tokens[idx]
                    print(f"⚠️ Failed to send to token {failed_token[:20]}... Error: {resp.exception}")
                    # Mark token as inactive
                    FCMToken.objects.filter(token=failed_token).update(is_active=False)
        
    except Exception as e:
        print(f"❌ Error sending FCM notification: {e}")


def check_and_send_alerts(device: Device, current_reading: WaterReading) -> None:
    """
    Evaluate critical events and send push notifications with cooldown.
    Priority order: Pump Dry Run > Underground Low > Overhead Full
    """
    # Get tank levels (support both old and new format)
    if current_reading.tank_data:
        underground = next((t['level'] for t in current_reading.tank_data if t['name'] == 'Underground'), None)
        overhead = next((t['level'] for t in current_reading.tank_data if t['name'] == 'Overhead'), None)
    else:
        underground = current_reading.underground_level
        overhead = current_reading.overhead_level
    
    if underground is None or overhead is None:
        return
    
    pump_on = current_reading.pump_status

    # Priority 1: Pump Dry Run (CRITICAL)
    if pump_on and underground < 10:
        alert = 'PUMP_DRY_RUN'
        if _cooldown_ok(device, alert):
            _send_fcm_notification(
                device,
                '🚨 CRITICAL: Pump Dry Run!',
                f'{device.name or device.device_id}: Pump is running but underground tank is at {underground}%. Pump protection activated.'
            )
            _mark_alert_sent(device, alert)
        return

    # Priority 2: Underground Low
    if underground < 15:
        alert = 'UNDERGROUND_LOW'
        if _cooldown_ok(device, alert):
            _send_fcm_notification(
                device,
                '⚠️ Underground Tank Low',
                f'{device.name or device.device_id}: Underground tank is at {underground}%. Consider refilling soon.'
            )
            _mark_alert_sent(device, alert)
        return

    # Priority 3: Overhead Full
    if overhead > 95:
        alert = 'OVERHEAD_FULL'
        if _cooldown_ok(device, alert):
            _send_fcm_notification(
                device,
                '💧 Overhead Tank Full',
                f'{device.name or device.device_id}: Overhead tank is at {overhead}%. Pump will stop to prevent overflow.'
            )
            _mark_alert_sent(device, alert)
        return


def send_offline_alert(device: Device) -> None:
    """Send notification when device goes offline."""
    now = timezone.now()
    alert_type = "DEVICE_OFFLINE"
    
    if _cooldown_ok(device, alert_type):
        _send_fcm_notification(
            device,
            '📡 Device Offline',
            f'{device.name or device.device_id} has been offline for more than 15 minutes. Check your internet connection.'
        )
        _mark_alert_sent(device, alert_type)
