from django.contrib import admin
from .models import Device, WaterReading, DailyWaterUsage
from django.urls import path
from django.contrib import admin
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta

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


# --- Custom Analytics Dashboard ---
class AnalyticsAdminSite(admin.AdminSite):
    site_header = 'AquaSavvy Solution Admin'

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('analytics/', self.admin_view(self.analytics_view), name='analytics_dashboard'),
        ]
        return custom + urls

    def analytics_view(self, request):
        # Last 30 days
        end_day = timezone.localdate()
        start_day = end_day - timedelta(days=30)
        qs = DailyWaterUsage.objects.filter(day__gte=start_day, day__lte=end_day)

        # Table: daily totals across all devices
        daily_totals = {}
        for row in qs.values('day').order_by('day'):
            d = row['day']
            total = qs.filter(day=d).aggregate(models.Sum('total_usage_liters'))['total_usage_liters__sum'] or 0
            daily_totals[str(d)] = total

        # Pie: totals by device (device_id only)
        by_device = {}
        for row in qs.values('device__device_id').order_by('device__device_id').distinct():
            did = row['device__device_id']
            total = qs.filter(device__device_id=did).aggregate(models.Sum('total_usage_liters'))['total_usage_liters__sum'] or 0
            by_device[did] = total

        context = dict(
            self.each_context(request),
            daily_totals=daily_totals,
            by_device=by_device,
        )
        return render(request, 'admin/analytics_dashboard.html', context)


admin_site = AnalyticsAdminSite()
