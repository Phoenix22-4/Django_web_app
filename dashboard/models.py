# dashboard/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# --- NEW: A PROFILE FOR EACH USER TO STORE PUSH TOKENS ---
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True) # Kept from previous
    # We will also need to store push notification tokens here
    # GCMDevice or WebPushDevice from 'push_notifications' will handle this

    def __str__(self):
        return f'{self.user.username} Profile'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)


class Device(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    device_id = models.CharField(max_length=100, unique=True, primary_key=True)
    name = models.CharField(max_length=100, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    # --- NEW FIELDS FOR ADMIN ---
    tank_capacity_liters = models.PositiveIntegerField(default=1000, help_text="Total capacity of the main user tank in Liters.")
    pump_present = models.BooleanField(default=True, help_text="Set to False if this is a monitor-only device with no pump.")

    # --- NEW FIELDS FOR NOTIFICATION COOLDOWN ---
    last_alert_type = models.CharField(max_length=50, blank=True, null=True)
    last_alert_sent_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name or self.device_id

class WaterReading(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='readings')
    timestamp = models.DateTimeField(auto_now_add=True)
    pump_status = models.BooleanField(default=False)
    
    # --- RENAMED & CHANGED ---
    pump_current_amps = models.FloatField(default=0.0) 

    # --- NEW DYNAMIC TANK FIELD ---
    # This JSONField will store: 
    # [{"name": "Tank 1", "level": 80}, {"name": "Tank 2", "level": 30}]
    tank_data = models.JSONField(default=list) 

    # --- REMOVED ---
    # overhead_level = models.IntegerField()
    # underground_level = models.IntegerField()
    # system_status = models.CharField(max_length=100)
    # pump_current = models.FloatField(default=0.0)

    def __str__(self):
        return f"Reading for {self.device.device_id} at {self.timestamp}"


# --- NEW MODEL FOR USER AUTOMATION ---
class AutomationRule(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='rules')
    name = models.CharField(max_length=100, default="My Rule")
    start_time = models.TimeField()
    end_time = models.TimeField()
    monitor_tank_name = models.CharField(max_length=100, default="Overhead", blank=True, help_text="The 'name' of the tank to monitor (e.g., 'Overhead')") 
    min_level = models.PositiveIntegerField(default=20, help_text="Pump ON when level is BELOW this %")
    max_level = models.PositiveIntegerField(default=95, help_text="Pump OFF when level is ABOVE this %")
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"Rule '{self.name}' for {self.device.device_id}"


# --- NEW MODEL FOR DATA ANALYTICS ---
class DailyWaterUsage(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='daily_usage')
    date = models.DateField()
    total_user_water_liters = models.FloatField(default=0.0)
    total_stored_water_liters = models.FloatField(default=0.0)
    total_power_kwh = models.FloatField(default=0.0)

    class Meta:
        ordering = ['-date']
        # Ensure only one entry per device per day
        unique_together = ('device', 'date') 

    def __str__(self):
        return f"Usage for {self.device.device_id} on {self.date}"

# Add a property to User model to safely access profile
from django.contrib.auth.models import User

def get_user_profile(self):
    try:
        return self.profile
    except Profile.DoesNotExist:
        return Profile.objects.create(user=self)

User.add_to_class('get_profile', get_user_profile)