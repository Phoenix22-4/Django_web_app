from django.contrib import admin
from .models import Device, WaterReading, DailyWaterUsage, Profile, AutomationRule, FCMToken
from django.urls import path
from django.shortcuts import render
from django.utils import timezone
from django.db import models
from datetime import timedelta
import json

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
    list_display = ('device', 'timestamp', 'overhead_level', 'underground_level', 'pump_status', 'pump_mode')
    list_filter = ('device', 'pump_mode')
    date_hierarchy = 'timestamp'
    readonly_fields = ('tank_data_display',)
    
    def tank_data_display(self, obj):
        if obj.tank_data:
            return json.dumps(obj.tank_data, indent=2)
        return "No tank data"
    tank_data_display.short_description = "Tank Data (JSON)"


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    search_fields = ('user__username', 'phone_number')


class AutomationRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'device', 'start_time', 'end_time', 'min_level', 'max_level', 'enabled')
    list_filter = ('enabled', 'device')
    search_fields = ('name', 'device__name', 'device__device_id')
    fieldsets = (
        (None, {
            'fields': ('device', 'name', 'enabled')
        }),
        ('Time Schedule', {
            'fields': ('start_time', 'end_time')
        }),
        ('Tank Levels', {
            'fields': ('destination_tank', 'min_level', 'max_level'),
            'description': 'Pump turns ON at min_level and OFF at max_level for the destination tank'
        }),
    )


class DailyWaterUsageAdmin(admin.ModelAdmin):
    list_display = ('device', 'day', 'total_usage_liters', 'total_stored_liters', 'total_power_kwh', 'pump_runtime_hours')
    list_filter = ('device', 'day')
    date_hierarchy = 'day'


class FCMTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_type', 'is_active', 'created_at', 'last_used', 'token_preview')
    list_filter = ('is_active', 'device_type')
    search_fields = ('user__username', 'token')
    readonly_fields = ('created_at', 'last_used', 'token')
    
    def token_preview(self, obj):
        return f"{obj.token[:30]}..." if len(obj.token) > 30 else obj.token
    token_preview.short_description = "Token Preview"


admin.site.register(Device, DeviceAdmin)
admin.site.register(WaterReading, WaterReadingAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(AutomationRule, AutomationRuleAdmin)
admin.site.register(DailyWaterUsage, DailyWaterUsageAdmin)
admin.site.register(FCMToken, FCMTokenAdmin)


# ==================== CUSTOM ADMIN ANALYTICS DASHBOARD ====================
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
import csv

@staff_member_required
def analytics_dashboard_view(request):
    """Custom admin view for water usage analytics"""
    from datetime import date, timedelta
    from django.db.models import Sum
    
    today = date.today()
    start_date = today - timedelta(days=30)
    
    # Get all daily usage data for last 30 days
    daily_usage_qs = DailyWaterUsage.objects.filter(day__gte=start_date, day__lte=today).order_by('day')
    
    # Calculate summary stats
    total_stats = daily_usage_qs.aggregate(
        total_usage=Sum('total_usage_liters'),
        total_power=Sum('total_power_kwh'),
        total_runtime=Sum('pump_runtime_hours')
    )
    
    # Get usage by device
    device_stats = daily_usage_qs.values('device__device_id', 'device__name') \
                                .annotate(
                                    total_usage=Sum('total_usage_liters'),
                                    total_power=Sum('total_power_kwh')
                                ).order_by('device__device_id')
    
    device_labels = []
    device_usage = []
    device_power = []
    for stat in device_stats:
        label = stat['device__name'] or stat['device__device_id']
        device_labels.append(label)
        device_usage.append(stat['total_usage'] or 0)
        device_power.append(float(stat['total_power'] or 0))
    
    # Get daily totals for line chart
    daily_totals = {}
    for entry in daily_usage_qs:
        day_str = entry.day.strftime('%Y-%m-%d')
        if day_str not in daily_totals:
            daily_totals[day_str] = {'usage': 0, 'stored': 0, 'power': 0, 'runtime': 0}
        daily_totals[day_str]['usage'] += entry.total_usage_liters
        daily_totals[day_str]['stored'] += entry.total_stored_liters
        daily_totals[day_str]['power'] += entry.total_power_kwh
        daily_totals[day_str]['runtime'] += entry.pump_runtime_hours
    
    daily_dates = list(daily_totals.keys())
    daily_usage_values = [daily_totals[d]['usage'] for d in daily_dates]
    
    # Prepare data for template
    daily_data = []
    for day_str in daily_dates:
        daily_data.append({
            'day': day_str,
            'total_usage': daily_totals[day_str]['usage'],
            'total_stored': daily_totals[day_str]['stored'],
            'total_power': daily_totals[day_str]['power'],
            'total_runtime': daily_totals[day_str]['runtime']
        })
    
    context = {
        **admin.site.each_context(request),
        'title': 'Water Usage Analytics',
        'total_usage_liters': total_stats['total_usage'] or 0,
        'total_power_kwh': total_stats['total_power'] or 0,
        'total_runtime_hours': total_stats['total_runtime'] or 0,
        'active_devices': Device.objects.filter(owner__isnull=False).count(),
        'device_labels': json.dumps(device_labels),
        'device_usage': json.dumps(device_usage),
        'device_power': json.dumps(device_power),
        'daily_dates': json.dumps(daily_dates),
        'daily_usage': json.dumps(daily_usage_values),
        'daily_data': daily_data,
    }
    
    return render(request, 'admin/analytics.html', context)


@staff_member_required
def download_analytics_csv(request):
    """Download last 30 days of water usage data as CSV"""
    from datetime import date, timedelta
    
    today = date.today()
    start_date = today - timedelta(days=30)
    
    daily_usage_qs = DailyWaterUsage.objects.filter(day__gte=start_date, day__lte=today).order_by('day', 'device__device_id')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="aquasavvy_analytics_30days.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Device ID', 'Device Name', 'Usage (L)', 'Stored (L)', 'Power (kWh)', 'Runtime (h)'])
    
    for entry in daily_usage_qs:
        writer.writerow([
            entry.day.strftime('%Y-%m-%d'),
            entry.device.device_id,
            entry.device.name or 'N/A',
            entry.total_usage_liters,
            entry.total_stored_liters,
            round(entry.total_power_kwh, 2),
            round(entry.pump_runtime_hours, 1)
        ])
    
    return response


# Add to admin site's URL patterns
from django.urls import path as url_path

# Create custom admin URLs
def get_admin_urls(original_urls):
    """Inject custom analytics URLs into admin"""
    custom_urls = [
        url_path('analytics/', analytics_dashboard_view, name='analytics_dashboard'),
        url_path('analytics/download-csv/', download_analytics_csv, name='download_analytics_csv'),
    ]
    return custom_urls + original_urls

# Monkey patch admin site URLs
admin.site.get_urls = lambda: get_admin_urls(admin.site.get_urls.__wrapped__(admin.site))
admin.site.get_urls.__wrapped__ = admin.site.__class__.get_urls
