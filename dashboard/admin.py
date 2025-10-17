# dashboard/admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.db.models import Sum, Count
from .models import Device, WaterReading, Profile, AutomationRule, DailyWaterUsage
import csv
from django.http import HttpResponse
import datetime
import json

class DeviceAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'name', 'owner', 'created_at', 'pump_present', 'tank_capacity_liters')
    readonly_fields = ('device_id', 'created_at')
    search_fields = ('device_id', 'name', 'owner__username')
    list_filter = ('owner', 'pump_present')
    fieldsets = (
        (None, {
            'fields': ('device_id', 'name', 'owner')
        }),
        ('Hardware Configuration', {
            'fields': ('tank_capacity_liters', 'pump_present')
        }),
        ('Date Information', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    # --- ADD THIS to create the custom admin page URL ---
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'analytics/',
                self.admin_site.admin_view(self.analytics_view),
                name='analytics_dashboard'
            ),
            path(
                'analytics/download_csv/',
                self.admin_site.admin_view(self.download_csv),
                name='download_analytics_csv'
            ),
        ]
        return custom_urls + urls

    # --- NEW VIEW for the analytics page ---
    def analytics_view(self, request):
        thirty_days_ago = datetime.date.today() - datetime.timedelta(days=30)
        data = DailyWaterUsage.objects.filter(date__gte=thirty_days_ago)

        # Pie Chart: Usage by Device
        pie_data_query = data.values('device__device_id').annotate(total=Sum('total_user_water_liters')).order_by('-total')
        pie_labels = [item['device__device_id'] for item in pie_data_query]
        pie_data = [item['total'] for item in pie_data_query]

        # Line Chart: Usage Over Time
        line_data_by_date = data.values('date').annotate(
            total_user=Sum('total_user_water_liters'),
            total_stored=Sum('total_stored_water_liters'),
            total_power=Sum('total_power_kwh')
        ).order_by('date')
        
        line_labels = [item['date'].strftime('%Y-%m-%d') for item in line_data_by_date]
        line_user_data = [item['total_user'] for item in line_data_by_date]
        line_stored_data = [item['total_stored'] for item in line_data_by_date]
        line_power_data = [item['total_power'] for item in line_data_by_date]

        context = {
            **self.admin_site.each_context(request),
            'title': 'Usage Analytics',
            'pie_labels': json.dumps(pie_labels),
            'pie_data': json.dumps(pie_data),
            'line_labels': json.dumps(line_labels),
            'line_user_data': json.dumps(line_user_data),
            'line_stored_data': json.dumps(line_stored_data),
            'line_power_data': json.dumps(line_power_data),
        }
        return render(request, 'admin/analytics_dashboard.html', context)

    # --- NEW VIEW for the CSV download ---
    def download_csv(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="aquasavvy_30_day_report.csv"'
        writer = csv.writer(response)
        
        writer.writerow(['Device ID (Anonymized)', 'Date', 'Total User Water (Liters)', 'Total Stored Water (Liters)', 'Total Power (kWh)'])
        
        thirty_days_ago = datetime.date.today() - datetime.timedelta(days=30)
        data = DailyWaterUsage.objects.filter(date__gte=thirty_days_ago).order_by('date', 'device')
        
        for row in data:
            writer.writerow([
                row.device.device_id, 
                row.date, 
                row.total_user_water_liters, 
                row.total_stored_water_liters,
                row.total_power_kwh
            ])
            
        return response

class WaterReadingAdmin(admin.ModelAdmin):
    # Updated to use new fields
    list_display = ('device', 'timestamp', 'pump_status', 'pump_current_amps', 'tank_data')
    list_filter = ('device',)
    date_hierarchy = 'timestamp'

# --- NEW: ADMINS for Profile and new models ---
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')

class AutomationRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'device', 'start_time', 'end_time', 'monitor_tank_name', 'min_level', 'max_level', 'enabled')
    list_filter = ('device', 'enabled')

class DailyWaterUsageAdmin(admin.ModelAdmin):
    list_display = ('date', 'device', 'total_user_water_liters', 'total_power_kwh')
    list_filter = ('device',)
    date_hierarchy = 'date'


admin.site.register(Device, DeviceAdmin)
admin.site.register(WaterReading, WaterReadingAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(AutomationRule, AutomationRuleAdmin)
admin.site.register(DailyWaterUsage, DailyWaterUsageAdmin)