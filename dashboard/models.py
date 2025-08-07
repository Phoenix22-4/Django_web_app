from django.db import models
from django.contrib.auth.models import User

class Device(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    device_id = models.CharField(max_length=100, unique=True, primary_key=True)
    name = models.CharField(max_length=100, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

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
