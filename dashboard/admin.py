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
    readonly_fields = ('device_id', 'created_at', 'tank_1_reading_id', 'tank_2_reading_id', 'tank_3_reading_id', 'tank_4_reading_id', 'solenoid_1_reading_id', 'solenoid_2_reading_id', 'solenoid_3_reading_id', 'solenoid_4_reading_id')
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
                ('tank_1_reading_id', 'tank_1_name', 'tank_1_is_source', 'tank_1_capacity_liters'),
                ('tank_2_reading_id', 'tank_2_name', 'tank_2_is_source', 'tank_2_capacity_liters'),
                ('tank_3_reading_id', 'tank_3_name', 'tank_3_is_source', 'tank_3_capacity_liters'),
                ('tank_4_reading_id', 'tank_4_name', 'tank_4_is_source', 'tank_4_capacity_liters'),
            ),
            'description': 'Reading IDs are auto-detected from IoT data. Enter tank names only for tanks with reading IDs. Check "Is Source" for the water supply tank. Set capacity in liters for each tank.'
        }),
        ('Solenoid Valve Configuration (Auto-detected from IoT data)', {
            'fields': (
                ('solenoid_1_reading_id', 'solenoid_1_name'),
                ('solenoid_2_reading_id', 'solenoid_2_name'),
                ('solenoid_3_reading_id', 'solenoid_3_name'),
                ('solenoid_4_reading_id', 'solenoid_4_name'),
            ),
            'description': 'Reading IDs are auto-detected from IoT data. Enter solenoid valve names only for valves with reading IDs.',
            'classes': ('collapse',)
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
            path(
                'analytics/download_csv/water_usage/',
                self.admin_site.admin_view(self.download_csv_water_usage),
                name='download_csv_water_usage'
            ),
            path(
                'analytics/download_csv/power_runtime/',
                self.admin_site.admin_view(self.download_csv_power_runtime),
                name='download_csv_power_runtime'
            ),
        ]
        return custom_urls + urls

    # --- NEW VIEW for the analytics page ---
    def analytics_view(self, request):
        thirty_days_ago = datetime.date.today() - datetime.timedelta(days=30)
        data = DailyWaterUsage.objects.filter(date__gte=thirty_days_ago)

        # Calculate totals
        total_usage_liters = data.aggregate(total=Sum('total_user_water_liters'))['total'] or 0
        total_power_kwh = data.aggregate(total=Sum('total_power_kwh'))['total'] or 0
        total_runtime_hours = data.aggregate(total=Sum('total_pump_runtime_hours'))['total'] or 0
        active_devices = data.values('device').distinct().count()

        # Device usage data for pie charts
        device_data = data.values('device__device_id').annotate(
            total_usage=Sum('total_user_water_liters'),
            total_power=Sum('total_power_kwh')
        ).order_by('-total_usage')
        
        device_labels = [item['device__device_id'] for item in device_data]
        device_usage = [item['total_usage'] for item in device_data]
        device_power = [item['total_power'] for item in device_data]

        # Daily data for line chart and table
        daily_data = data.values('date').annotate(
            total_usage=Sum('total_user_water_liters'),
            total_stored=Sum('total_stored_water_liters'),
            total_power=Sum('total_power_kwh'),
            total_runtime=Sum('total_pump_runtime_hours')
        ).order_by('date')
        
        daily_dates = [item['date'].strftime('%Y-%m-%d') for item in daily_data]
        daily_usage = [item['total_usage'] for item in daily_data]

        context = {
            **self.admin_site.each_context(request),
            'title': 'Usage Analytics',
            'total_usage_liters': total_usage_liters,
            'total_power_kwh': total_power_kwh,
            'total_runtime_hours': total_runtime_hours,
            'active_devices': active_devices,
            'device_labels': json.dumps(device_labels),
            'device_usage': json.dumps(device_usage),
            'device_power': json.dumps(device_power),
            'daily_dates': json.dumps(daily_dates),
            'daily_usage': json.dumps(daily_usage),
            'daily_data': daily_data,
        }
        return render(request, 'admin/analytics.html', context)

    # --- COMPREHENSIVE CSV DOWNLOAD VIEWS ---
    def download_csv(self, request):
        """Download comprehensive 30-day report"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="aquasavvy_30_day_comprehensive_report.csv"'
        writer = csv.writer(response)
        
        writer.writerow(['Device ID', 'Date', 'Water Usage (L)', 'Water Stored (L)', 'Power (kWh)', 'Pump Runtime (h)'])
        
        thirty_days_ago = datetime.date.today() - datetime.timedelta(days=30)
        data = DailyWaterUsage.objects.filter(date__gte=thirty_days_ago).order_by('date', 'device')
        
        for row in data:
            writer.writerow([
                row.device.device_id, 
                row.date, 
                row.total_user_water_liters, 
                row.total_stored_water_liters,
                row.total_power_kwh,
                row.total_pump_runtime_hours
            ])
            
        return response

    def download_csv_water_usage(self, request):
        """Download water usage data only"""
        period = request.GET.get('period', 'daily')
        response = HttpResponse(content_type='text/csv')
        
        if period == 'daily':
            filename = "aquasavvy_water_usage_daily.csv"
            days_ago = 30
        elif period == 'monthly':
            filename = "aquasavvy_water_usage_monthly.csv"
            days_ago = 365
        else:  # yearly
            filename = "aquasavvy_water_usage_yearly.csv"
            days_ago = 1095  # 3 years
        
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        writer = csv.writer(response)
        
        writer.writerow(['Device ID', 'Date', 'Water Usage (L)', 'Water Stored (L)'])
        
        start_date = datetime.date.today() - datetime.timedelta(days=days_ago)
        data = DailyWaterUsage.objects.filter(date__gte=start_date).order_by('date', 'device')
        
        for row in data:
            writer.writerow([
                row.device.device_id, 
                row.date, 
                row.total_user_water_liters, 
                row.total_stored_water_liters
            ])
            
        return response

    def download_csv_power_runtime(self, request):
        """Download power and pump runtime data"""
        period = request.GET.get('period', 'daily')
        response = HttpResponse(content_type='text/csv')
        
        if period == 'daily':
            filename = "aquasavvy_power_runtime_daily.csv"
            days_ago = 30
        elif period == 'monthly':
            filename = "aquasavvy_power_runtime_monthly.csv"
            days_ago = 365
        else:  # yearly
            filename = "aquasavvy_power_runtime_yearly.csv"
            days_ago = 1095  # 3 years
        
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        writer = csv.writer(response)
        
        writer.writerow(['Device ID', 'Date', 'Power (kWh)', 'Pump Runtime (h)'])
        
        start_date = datetime.date.today() - datetime.timedelta(days=days_ago)
        data = DailyWaterUsage.objects.filter(date__gte=start_date).order_by('date', 'device')
        
        for row in data:
            writer.writerow([
                row.device.device_id, 
                row.date, 
                row.total_power_kwh,
                row.total_pump_runtime_hours
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
    
    def changelist_view(self, request, extra_context=None):
        # Redirect to analytics view when clicking on Usage
        from django.shortcuts import redirect
        return redirect('admin:analytics_dashboard')


admin.site.register(Device, DeviceAdmin)
admin.site.register(WaterReading, WaterReadingAdmin)
admin.site.register(DailyWaterUsage, DailyWaterUsageAdmin)