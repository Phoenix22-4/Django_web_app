from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from .models import Device, WaterReading

# If using django-push-notifications, you would typically use APNSDevice/FCMDevice models.
try:
    from push_notifications.models import FCMDevice
except Exception:  # library may not be installed locally yet
    FCMDevice = None

ALERT_COOLDOWN_MINUTES = 60

def _cooldown_ok(device: Device, alert_type: str) -> bool:
    if not device.last_alert_type or not device.last_alert_sent_at:
        return True
    if device.last_alert_type != alert_type:
        return True
    return device.last_alert_sent_at <= timezone.now() - timedelta(minutes=ALERT_COOLDOWN_MINUTES)

def _mark_alert_sent(device: Device, alert_type: str) -> None:
    device.last_alert_type = alert_type
    device.last_alert_sent_at = timezone.now()
    device.save(update_fields=['last_alert_type', 'last_alert_sent_at'])

def _send_push_to_owner(device: Device, title: str, body: str) -> None:
    if not device.owner:
        return
    if FCMDevice is None:
        return
    devices = FCMDevice.objects.filter(user=device.owner)
    if devices.exists():
        devices.send_message(title=title, body=body)

def check_and_send_alerts(device: Device, current_reading: WaterReading) -> None:
    """Evaluate critical events and send push notifications with cooldown."""
    underground = current_reading.underground_level
    overhead = current_reading.overhead_level
    pump_on = current_reading.pump_status

    # Priority 1: Pump Dry Run
    if pump_on and underground < 10:
        alert = 'PUMP_DRY_RUN'
        if _cooldown_ok(device, alert):
            _send_push_to_owner(device, 'Pump Dry-Run Protection', 'Pump stopped: Underground tank is too low.')
            _mark_alert_sent(device, alert)
        return

    # Priority 2: Underground Low
    if underground < 15:
        alert = 'UNDERGROUND_LOW'
        if _cooldown_ok(device, alert):
            _send_push_to_owner(device, 'Underground Tank Low', 'Underground tank is below 15%. Consider refilling.')
            _mark_alert_sent(device, alert)
        return

    # Priority 3: Overhead Full
    if overhead > 95:
        alert = 'OVERHEAD_FULL'
        if _cooldown_ok(device, alert):
            _send_push_to_owner(device, 'Overhead Tank Full', 'Overhead tank is above 95%. Pump will stop to prevent overflow.')
            _mark_alert_sent(device, alert)
        return

