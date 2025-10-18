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
    readonly_fields = ('device_id', 'created_at', 'tank_1_reading_id', 'tank_2_reading_id', 'tank_3_reading_id', 'tank_4_reading_id')
    search_fields = ('device_id', 'name', 'owner__username')
    list_filter = ('owner', 'pump_present')
    fieldsets = (
        (None, {
            'fields': ('device_id', 'name', 'owner')
        }),
        ('Hardware Configuration', {
            'fields': ('tank_capacity_liters', 'pump_present')
        }),
        ('System Parameters', {
            'fields': ('overload_current_amps', 'dry_run_current_amps'),
            'description': 'Current thresholds for pump protection and status messages.'
        }),
        ('Tank Configuration (Auto-detected from IoT data)', {
            'fields': (
                ('tank_1_reading_id', 'tank_1_name'),
                ('tank_2_reading_id', 'tank_2_name'),
                ('tank_3_reading_id', 'tank_3_name'),
                ('tank_4_reading_id', 'tank_4_name'),
            ),
            'description': 'Reading IDs are auto-detected from IoT data. Enter tank names only for tanks with reading IDs.'
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
    list_display = ('device', 'timestamp', 'get_dynamic_columns')
    list_filter = ('device',)
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)
    
    def get_dynamic_columns(self, obj):
        """Display dynamic columns based on system_data"""
        if not obj.system_data:
            return "No data"
        
        # Get all keys from system_data and display them
        columns = []
        for key, value in obj.system_data.items():
            if key.endswith('_level'):
                columns.append(f"{key}: {value}%")
            elif key == 'pump_status':
                status = "ON" if value else "OFF"
                columns.append(f"Pump: {status}")
            elif key == 'pump_current':
                columns.append(f"Current: {value}A")
            elif key == 'system_status':
                columns.append(f"Status: {value}")
            else:
                columns.append(f"{key}: {value}")
        
        return " | ".join(columns)
    
    get_dynamic_columns.short_description = 'System Data'
    
    def get_list_display(self, request):
        """Dynamically add columns based on recent data"""
        base_display = ['device', 'timestamp', 'get_dynamic_columns']
        
        # Get recent readings to determine dynamic columns
        recent_readings = WaterReading.objects.order_by('-timestamp')[:10]
        if recent_readings:
            # Get all unique keys from recent system_data
            all_keys = set()
            for reading in recent_readings:
                if reading.system_data:
                    all_keys.update(reading.system_data.keys())
            
            # Add dynamic columns (limit to 7 max as requested)
            dynamic_columns = list(all_keys)[:7]
            for key in dynamic_columns:
                method_name = f'get_{key}'
                if not hasattr(self, method_name):
                    setattr(self, method_name, self._create_dynamic_column_method(key))
                base_display.append(method_name)
        
        return base_display
    
    def _create_dynamic_column_method(self, key):
        """Create a dynamic method for displaying a column"""
        def method(obj):
            return obj.system_data.get(key, 'N/A')
        method.short_description = key.replace('_', ' ').title()
        method.admin_order_field = f'system_data__{key}'
        return method

# --- NEW: ADMINS for new models ---
class DailyWaterUsageAdmin(admin.ModelAdmin):
    list_display = ('date', 'device', 'total_user_water_liters', 'total_power_kwh')
    list_filter = ('device',)
    date_hierarchy = 'date'


admin.site.register(Device, DeviceAdmin)
admin.site.register(WaterReading, WaterReadingAdmin)
admin.site.register(DailyWaterUsage, DailyWaterUsageAdmin)