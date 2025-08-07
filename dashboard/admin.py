from django.contrib import admin
from .models import Device, WaterReading

class DeviceAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'name', 'owner', 'created_at')
    readonly_fields = ('device_id', 'created_at')
    search_fields = ('device_id', 'name', 'owner__username')
    list_filter = ('owner',)
    fieldsets = (
        (None, {
            'fields': ('device_id', 'name', 'owner')
        }),
        ('Date Information', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

class WaterReadingAdmin(admin.ModelAdmin):
    list_display = ('device', 'timestamp', 'overhead_level', 'underground_level', 'pump_status')
    list_filter = ('device',)
    date_hierarchy = 'timestamp'

admin.site.register(Device, DeviceAdmin)
admin.site.register(WaterReading, WaterReadingAdmin)
