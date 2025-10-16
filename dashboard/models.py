from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import time

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
    # NEW: Dynamic tank support - stores array of tanks like [{"name": "Underground", "level": 30}, ...]
    tank_data = models.JSONField(default=list, blank=True)
    # LEGACY FIELDS: Keep for backward compatibility during migration
    overhead_level = models.IntegerField(default=0, null=True, blank=True)
    underground_level = models.IntegerField(default=0, null=True, blank=True)
    # Pump data
    pump_status = models.BooleanField(default=False)
    pump_current_amps = models.FloatField(default=0.0)  # Renamed for clarity
    pump_mode = models.CharField(max_length=50, default='AUTO')  # AUTO, MANUAL, TIMESLOT
    system_status = models.CharField(max_length=100, default='OK')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reading for {self.device.device_id} at {self.timestamp}"
    
    def get_tank_by_name(self, tank_name):
        """Helper to find a specific tank in tank_data array"""
        for tank in self.tank_data:
            if tank.get('name') == tank_name:
                return tank
        return None


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=30, blank=True, default="")

    def __str__(self):
        return f"Profile for {self.user.username}"


class AutomationRule(models.Model):
    """User-defined automation rules for pump control based on time slots"""
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='automation_rules')
    name = models.CharField(max_length=100, help_text="e.g., 'Night Time Pumping'")
    start_time = models.TimeField(help_text="When this rule becomes active")
    end_time = models.TimeField(help_text="When this rule becomes inactive")
    min_level = models.IntegerField(help_text="Pump ON when destination tank reaches this level (%)")
    max_level = models.IntegerField(help_text="Pump OFF when destination tank reaches this level (%)")
    destination_tank = models.CharField(max_length=50, default="Overhead", help_text="Which tank to monitor")
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.name} ({self.start_time}-{self.end_time})"
    
    def is_active_now(self):
        """Check if this rule is active at the current time"""
        if not self.enabled:
            return False
        now = timezone.now().time()
        if self.start_time <= self.end_time:
            # Normal case: 08:00 - 18:00
            return self.start_time <= now <= self.end_time
        else:
            # Overnight case: 22:00 - 06:00
            return now >= self.start_time or now <= self.end_time


class DailyWaterUsage(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='daily_usage')
    day = models.DateField()
    total_usage_liters = models.IntegerField(default=0)
    total_stored_liters = models.IntegerField(default=0)  # Underground tank refill
    total_power_kwh = models.FloatField(default=0.0)  # Power consumption
    pump_runtime_hours = models.FloatField(default=0.0)  # Total hours pump was ON

    class Meta:
        unique_together = ('device', 'day')
        indexes = [
            models.Index(fields=['day']),
        ]

    def __str__(self):
        return f"{self.device.device_id} - {self.day}: {self.total_usage_liters}L, {self.total_power_kwh}kWh"
