# dashboard/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# --- NEW: A PROFILE FOR EACH USER TO STORE PUSH TOKENS ---
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True) # Kept from previous
    fcm_token = models.TextField(blank=True, null=True, help_text="Firebase Cloud Messaging token for push notifications")
    push_notifications_enabled = models.BooleanField(default=True, help_text="Enable/disable push notifications")
    last_notification_sent = models.DateTimeField(blank=True, null=True)

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
    
    # --- SYSTEM PARAMETERS ---
    overload_current_amps = models.FloatField(default=15.0, help_text="Current threshold for overload detection (Amps)")
    dry_run_current_amps = models.FloatField(default=2.0, help_text="Current threshold for dry run detection (Amps)")

    # --- TANK CONFIGURATION FIELDS (Auto-populated from IoT data) ---
    tank_1_reading_id = models.CharField(max_length=100, blank=True, null=True, help_text="Reading ID for Tank 1 (auto-detected from IoT data)")
    tank_1_name = models.CharField(max_length=100, blank=True, null=True, help_text="Name for Tank 1 (enter only if reading_id exists)")
    tank_2_reading_id = models.CharField(max_length=100, blank=True, null=True, help_text="Reading ID for Tank 2 (auto-detected from IoT data)")
    tank_2_name = models.CharField(max_length=100, blank=True, null=True, help_text="Name for Tank 2 (enter only if reading_id exists)")
    tank_3_reading_id = models.CharField(max_length=100, blank=True, null=True, help_text="Reading ID for Tank 3 (auto-detected from IoT data)")
    tank_3_name = models.CharField(max_length=100, blank=True, null=True, help_text="Name for Tank 3 (enter only if reading_id exists)")
    tank_4_reading_id = models.CharField(max_length=100, blank=True, null=True, help_text="Reading ID for Tank 4 (auto-detected from IoT data)")
    tank_4_name = models.CharField(max_length=100, blank=True, null=True, help_text="Name for Tank 4 (enter only if reading_id exists)")

    # --- NEW FIELDS FOR NOTIFICATION COOLDOWN ---
    last_alert_type = models.CharField(max_length=50, blank=True, null=True)
    last_alert_sent_at = models.DateTimeField(blank=True, null=True)

    def get_tank_names(self):
        """Get list of tank names that have been set"""
        tank_names = []
        for i in range(1, 5):
            tank_name = getattr(self, f'tank_{i}_name', None)
            if tank_name:
                tank_names.append(tank_name)
        return tank_names
    
    def get_available_tank_slots(self):
        """Get list of available tank slots (1-4) that don't have names yet"""
        available = []
        for i in range(1, 5):
            tank_name = getattr(self, f'tank_{i}_name', None)
            if not tank_name:
                available.append(i)
        return available

    def __str__(self):
        return self.name or self.device_id

class WaterReading(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='readings')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # --- DYNAMIC SYSTEM DATA ---
    # This JSONField will store all dynamic data from IoT:
    # {"overhead_level": 68, "underground_level": 98, "pump_status": false, "pump_current": 0, "system_status": "Cloud Connected"}
    system_data = models.JSONField(default=dict) 

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