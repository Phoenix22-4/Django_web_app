from django.contrib import admin
from .models import Device, WaterReading
from django.utils.html import format_html

# This class customizes how the Device model is displayed in the admin panel.
class DeviceAdmin(admin.ModelAdmin):
    # These are the columns that will be displayed in the list of devices.
    list_display = ('device_id', 'name', 'owner', 'get_live_status', 'created_at')
    
    readonly_fields = ('device_id', 'created_at')
    search_fields = ('device_id', 'name', 'owner__username')
    list_filter = ('owner',)
    
    fieldsets = (
        (None, { 'fields': ('device_id', 'name', 'owner') }),
        ('Date Information', { 'fields': ('created_at',), 'classes': ('collapse',) }),
    )

    # --- THIS IS THE NEW FUNCTION FOR LIVE STATUS ---
    def get_live_status(self, obj):
        # Find the most recent reading for this device
        last_reading = obj.readings.order_by('-timestamp').first()
        if not last_reading:
            return "No data yet"
        
        # Create a color-coded status for the pump
        pump_status_text = "ON" if last_reading.pump_status else "OFF"
        pump_color = "green" if last_reading.pump_status else "red"
        
        # Format the output as HTML
        return format_html(
            f"<b>Overhead:</b> {last_reading.overhead_level}% | "
            f"<b>Underground:</b> {last_reading.underground_level}% | "
            f"<b>Pump:</b> <span style='color: {pump_color};'>{pump_status_text}</span>"
        )
    get_live_status.short_description = 'Live Status' # Column header

# This class customizes the WaterReading display.
class WaterReadingAdmin(admin.ModelAdmin):
    list_display = ('device', 'timestamp', 'overhead_level', 'underground_level', 'pump_status')
    list_filter = ('device',)
    date_hierarchy = 'timestamp'


# Register your models with their custom admin configurations.
admin.site.register(Device, DeviceAdmin)
admin.site.register(WaterReading, WaterReadingAdmin)
