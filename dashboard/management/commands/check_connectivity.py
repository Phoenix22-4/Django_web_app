from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from dashboard.models import Device, WaterReading
from dashboard.notifications import _cooldown_ok, _mark_alert_sent, _send_push_to_owner

class Command(BaseCommand):
    help = 'Send OFFLINE alerts for devices with no readings in 15+ minutes'

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(minutes=15)
        for device in Device.objects.all():
            last = device.readings.order_by('-timestamp').first()
            if not last or last.timestamp < cutoff:
                alert = 'OFFLINE_ALERT'
                if _cooldown_ok(device, alert):
                    _send_push_to_owner(device, 'Device Offline', f'Device {device.device_id} has been offline for 15+ minutes.')
                    _mark_alert_sent(device, alert)

