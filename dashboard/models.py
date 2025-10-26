# dashboard/models.py
from django.db import models
import json
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class DeviceFCMToken(models.Model):
    """Model to store FCM tokens with device ID tracking - no user dependency"""
    device_id = models.CharField(max_length=255, db_index=True, help_text="Unique device identifier (UUID or browser fingerprint)")
    fcm_token = models.TextField(unique=True, db_index=True, help_text="Firebase Cloud Messaging token")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Device FCM Token'
        verbose_name_plural = 'Device FCM Tokens'
    
    def __str__(self):
        return f'Device: {self.device_id[:20]}... - Token: {self.fcm_token[:20]}...'
    
    def get_device_owner(self):
        """Get the device owner for sending notifications"""
        try:
            device = Device.objects.get(device_id=self.device_id)
            return device.owner
        except Device.DoesNotExist:
            return None


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
    tank_1_is_source = models.BooleanField(default=False, help_text="Check if Tank 1 is the source tank (water supply)")
    tank_2_reading_id = models.CharField(max_length=100, blank=True, null=True, help_text="Reading ID for Tank 2 (auto-detected from IoT data)")
    tank_2_name = models.CharField(max_length=100, blank=True, null=True, help_text="Name for Tank 2 (enter only if reading_id exists)")
    tank_2_is_source = models.BooleanField(default=False, help_text="Check if Tank 2 is the source tank (water supply)")
    tank_3_reading_id = models.CharField(max_length=100, blank=True, null=True, help_text="Reading ID for Tank 3 (auto-detected from IoT data)")
    tank_3_name = models.CharField(max_length=100, blank=True, null=True, help_text="Name for Tank 3 (enter only if reading_id exists)")
    tank_3_is_source = models.BooleanField(default=False, help_text="Check if Tank 3 is the source tank (water supply)")
    tank_4_reading_id = models.CharField(max_length=100, blank=True, null=True, help_text="Reading ID for Tank 4 (auto-detected from IoT data)")
    tank_4_name = models.CharField(max_length=100, blank=True, null=True, help_text="Name for Tank 4 (enter only if reading_id exists)")
    tank_4_is_source = models.BooleanField(default=False, help_text="Check if Tank 4 is the source tank (water supply)")
    tank_4_capacity_liters = models.PositiveIntegerField(default=500, blank=True, null=True, help_text="Capacity of Tank 4 in liters")

    # --- TANK CAPACITY FIELDS ---
    tank_1_capacity_liters = models.PositiveIntegerField(default=500, blank=True, null=True, help_text="Capacity of Tank 1 in liters")
    tank_2_capacity_liters = models.PositiveIntegerField(default=500, blank=True, null=True, help_text="Capacity of Tank 2 in liters")
    tank_3_capacity_liters = models.PositiveIntegerField(default=500, blank=True, null=True, help_text="Capacity of Tank 3 in liters")

    # --- SOLENOID VALVE CONFIGURATION FIELDS (Auto-populated from IoT data) ---
    solenoid_1_reading_id = models.CharField(max_length=100, blank=True, null=True, help_text="Reading ID for Solenoid Valve 1 (auto-detected from IoT data)")
    solenoid_1_name = models.CharField(max_length=100, blank=True, null=True, help_text="Name for Solenoid Valve 1 (enter only if reading_id exists)")
    solenoid_2_reading_id = models.CharField(max_length=100, blank=True, null=True, help_text="Reading ID for Solenoid Valve 2 (auto-detected from IoT data)")
    solenoid_2_name = models.CharField(max_length=100, blank=True, null=True, help_text="Name for Solenoid Valve 2 (enter only if reading_id exists)")
    solenoid_3_reading_id = models.CharField(max_length=100, blank=True, null=True, help_text="Reading ID for Solenoid Valve 3 (auto-detected from IoT data)")
    solenoid_3_name = models.CharField(max_length=100, blank=True, null=True, help_text="Name for Solenoid Valve 3 (enter only if reading_id exists)")
    solenoid_4_reading_id = models.CharField(max_length=100, blank=True, null=True, help_text="Reading ID for Solenoid Valve 4 (auto-detected from IoT data)")
    solenoid_4_name = models.CharField(max_length=100, blank=True, null=True, help_text="Name for Solenoid Valve 4 (enter only if reading_id exists)")

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

    def get_solenoid_names(self):
        """Get list of solenoid valve names that have been set"""
        solenoid_names = []
        for i in range(1, 5):
            solenoid_name = getattr(self, f'solenoid_{i}_name', None)
            if solenoid_name:
                solenoid_names.append(solenoid_name)
        return solenoid_names
    
    def get_available_solenoid_slots(self):
        """Get list of available solenoid valve slots (1-4) that don't have names yet"""
        available = []
        for i in range(1, 5):
            solenoid_name = getattr(self, f'solenoid_{i}_name', None)
            if not solenoid_name:
                available.append(i)
        return available
    
    def get_source_tank_info(self):
        """Get information about the source tank"""
        for i in range(1, 5):
            is_source = getattr(self, f'tank_{i}_is_source', False)
            if is_source:
                reading_id = getattr(self, f'tank_{i}_reading_id', None)
                name = getattr(self, f'tank_{i}_name', None)
                if reading_id and name:
                    return {
                        'slot': i,
                        'reading_id': reading_id,
                        'name': name
                    }
        return None
    
    def get_secondary_tanks_info(self):
        """Get information about all secondary tanks (non-source tanks)"""
        secondary_tanks = []
        for i in range(1, 5):
            is_source = getattr(self, f'tank_{i}_is_source', False)
            if not is_source:
                reading_id = getattr(self, f'tank_{i}_reading_id', None)
                name = getattr(self, f'tank_{i}_name', None)
                if reading_id and name:
                    secondary_tanks.append({
                        'slot': i,
                        'reading_id': reading_id,
                        'name': name
                    })
        return secondary_tanks

    # ====== DASHBOARD CONFIG HELPERS (for dashboard.html JSON block) ======
    def get_tank_config(self):
        """
        Return a list of tank config dicts using admin configuration.
        Only include tanks that have BOTH a name and a reading_id.
        Each item: { "name": <display name>, "data_key": <reading_id>, "capacity": <capacity_liters> }
        """
        tanks = []
        for i in range(1, 5):
            name = getattr(self, f"tank_{i}_name", None)
            reading_id = getattr(self, f"tank_{i}_reading_id", None)
            capacity = getattr(self, f"tank_{i}_capacity_liters", 500) or 500
            if name and reading_id:
                tanks.append({
                    "name": name,
                    "data_key": reading_id,
                    "capacity": capacity
                })
        return tanks

    def get_tank_config_json(self):
        """JSON string for tanks, safe to embed in <script> tag."""
        return json.dumps(self.get_tank_config())

    def get_solenoid_config(self):
        """
        Return a list of solenoid config dicts using admin configuration.
        Only include solenoids that have BOTH a name and a reading_id.
        Each item: { "name": <display name>, "data_key": <reading_id> }
        """
        solenoids = []
        for i in range(1, 5):
            name = getattr(self, f"solenoid_{i}_name", None)
            reading_id = getattr(self, f"solenoid_{i}_reading_id", None)
            if name and reading_id:
                solenoids.append({
                    "name": name,
                    "data_key": reading_id
                })
        return solenoids

    def get_solenoid_config_json(self):
        """JSON string for solenoids, safe to embed in <script> tag."""
        return json.dumps(self.get_solenoid_config())

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


# --- NEW MODEL FOR DATA ANALYTICS ---
class DailyWaterUsage(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='daily_usage')
    date = models.DateField()
    total_user_water_liters = models.FloatField(default=0.0)
    total_stored_water_liters = models.FloatField(default=0.0)
    total_power_kwh = models.FloatField(default=0.0)
    total_pump_runtime_hours = models.FloatField(default=0.0)
    peak_hours = models.JSONField(default=list, blank=True)  # List of peak hours

    class Meta:
        ordering = ['-date']
        # Ensure only one entry per device per day
        unique_together = ('device', 'date')
        verbose_name = 'Usage'
        verbose_name_plural = 'Usage' 

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