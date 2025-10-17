# dashboard/management/commands/aggregate_daily_data.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum, Avg, Count
from dashboard.models import WaterReading, DailyWaterUsage, Device
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Aggregate daily water usage data and clean up old records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Get yesterday's date (we aggregate the previous day's data)
        yesterday = timezone.now().date() - timedelta(days=1)
        
        self.stdout.write(f'Processing data for {yesterday}')
        
        # Get all devices
        devices = Device.objects.all()
        total_aggregated = 0
        total_cleaned = 0
        
        for device in devices:
            # Aggregate yesterday's data for this device
            readings = WaterReading.objects.filter(
                device=device,
                timestamp__date=yesterday
            ).order_by('timestamp')
            
            if not readings.exists():
                continue
            
            # Calculate aggregated values
            total_readings = readings.count()
            pump_on_readings = readings.filter(pump_status=True).count()
            pump_runtime_hours = (pump_on_readings / total_readings) * 24 if total_readings > 0 else 0
            
            # Calculate power consumption (assuming 1.5kW pump)
            pump_power_kw = 1.5  # Typical water pump power
            total_power_kwh = pump_runtime_hours * pump_power_kw
            
            # Calculate water usage (simplified - in real implementation, you'd track actual flow)
            # For now, estimate based on pump runtime
            estimated_flow_rate = 50  # liters per minute (typical for household pumps)
            total_usage_liters = int(pump_runtime_hours * 60 * estimated_flow_rate)
            
            # Calculate stored water (water pumped from underground to overhead)
            total_stored_liters = total_usage_liters  # Simplified assumption
            
            if not dry_run:
                # Create or update daily usage record
                daily_usage, created = DailyWaterUsage.objects.get_or_create(
                    device=device,
                    day=yesterday,
                    defaults={
                        'total_usage_liters': total_usage_liters,
                        'total_stored_liters': total_stored_liters,
                        'total_power_kwh': total_power_kwh,
                        'pump_runtime_hours': pump_runtime_hours,
                    }
                )
                
                if not created:
                    # Update existing record
                    daily_usage.total_usage_liters = total_usage_liters
                    daily_usage.total_stored_liters = total_stored_liters
                    daily_usage.total_power_kwh = total_power_kwh
                    daily_usage.pump_runtime_hours = pump_runtime_hours
                    daily_usage.save()
                
                self.stdout.write(
                    f'  {device.device_id}: {total_usage_liters}L, {total_power_kwh:.2f}kWh, {pump_runtime_hours:.2f}h'
                )
            else:
                self.stdout.write(
                    f'  {device.device_id}: Would aggregate {total_usage_liters}L, {total_power_kwh:.2f}kWh, {pump_runtime_hours:.2f}h'
                )
            
            total_aggregated += 1
        
        # Clean up old data
        cutoff_date = timezone.now().date() - timedelta(days=2)  # Keep last 48 hours of raw data
        old_readings = WaterReading.objects.filter(timestamp__date__lt=cutoff_date)
        old_readings_count = old_readings.count()
        
        if old_readings_count > 0:
            if not dry_run:
                old_readings.delete()
                self.stdout.write(f'Deleted {old_readings_count} old readings (older than 48 hours)')
            else:
                self.stdout.write(f'Would delete {old_readings_count} old readings (older than 48 hours)')
            total_cleaned += old_readings_count
        
        # Clean up old daily summaries (keep last 35 days)
        daily_cutoff = timezone.now().date() - timedelta(days=35)
        old_daily = DailyWaterUsage.objects.filter(day__lt=daily_cutoff)
        old_daily_count = old_daily.count()
        
        if old_daily_count > 0:
            if not dry_run:
                old_daily.delete()
                self.stdout.write(f'Deleted {old_daily_count} old daily summaries (older than 35 days)')
            else:
                self.stdout.write(f'Would delete {old_daily_count} old daily summaries (older than 35 days)')
            total_cleaned += old_daily_count
        
        # Summary
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'DRY RUN COMPLETE: Would aggregate {total_aggregated} devices, clean {total_cleaned} records'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'COMPLETE: Aggregated {total_aggregated} devices, cleaned {total_cleaned} records'
                )
            )
