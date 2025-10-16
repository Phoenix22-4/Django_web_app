from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Device(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    device_id = models.CharField(max_length=100, unique=True, primary_key=True)
    name = models.CharField(max_length=100, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    # Alerts cooldown tracking
    last_alert_type = models.CharField(max_length=50, blank=True, null=True)
    last_alert_sent_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name or self.device_id

class WaterReading(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='readings')
    overhead_level = models.IntegerField()
    underground_level = models.IntegerField()
    pump_status = models.BooleanField()
    pump_current = models.FloatField(default=0.0)
    system_status = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reading for {self.device.device_id} at {self.timestamp}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=30, blank=True, default="")

    def __str__(self):
        return f"Profile for {self.user.username}"


class DailyWaterUsage(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='daily_usage')
    day = models.DateField()
    total_usage_liters = models.IntegerField(default=0)

    class Meta:
        unique_together = ('device', 'day')
        indexes = [
            models.Index(fields=['day']),
        ]

    def __str__(self):
        return f"{self.device.device_id} - {self.day}: {self.total_usage_liters} L"
