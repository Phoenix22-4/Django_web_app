# dashboard/management/commands/aggregate_daily_data.py
import datetime
from django.core.management.base import BaseCommand
from django.db.models import Avg, Sum, F, Count
from django.utils import timezone
from dashboard.models import Device, WaterReading, DailyWaterUsage

class Command(BaseCommand):
    help = 'Aggregates daily water and power usage and prunes old data.'

    def handle(self, *args, **options):
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        
        self.stdout.write(f'Starting daily aggregation for {yesterday}...')
        
        # 1. Find all devices
        for device in Device.objects.all():
            readings = WaterReading.objects.filter(device=device, timestamp__date=yesterday)
            
            if not readings.exists():
                self.stdout.write(f'No readings for {device.device_id}. Skipping.')
                continue

            # 2. Calculate Power Usage
            total_kwh = 0.0
            if device.pump_present:
                pump_on_readings = readings.filter(pump_status=True)
                # Assuming 1 reading every 5 seconds (12 readings per minute)
                total_runtime_minutes = pump_on_readings.count() / 12.0 
                
                if total_runtime_minutes > 0:
                    average_current = pump_on_readings.aggregate(Avg('pump_current_amps'))['pump_current_amps__avg']
                    if average_current is None: average_current = 0.0
                    
                    # P = I * V. Using 240V for Kenya.
                    # kWh = (Amps * Volts * Hours) / 1000
                    total_kwh = (average_current * 240 * (total_runtime_minutes / 60.0)) / 1000
                else:
                    total_kwh = 0.0

            # 3. Calculate Water Usage (Placeholder)
            # Real calculation is very complex. It requires knowing tank dimensions (from device.tank_capacity_liters)
            # and accurately tracking the *change* in level, which is hard.
            # We will store placeholder data for now.
            total_user_liters = 0.0 # Placeholder
            total_stored_liters = 0.0 # Placeholder

            # 4. Save the aggregated data
            DailyWaterUsage.objects.update_or_create(
                device=device,
                date=yesterday,
                defaults={
                    'total_user_water_liters': total_user_liters,
                    'total_stored_water_liters': total_stored_liters,
                    'total_power_kwh': total_kwh
                }
            )
            self.stdout.write(f'Aggregated data for {device.device_id} on {yesterday}. Power: {total_kwh} kWh')

        # 5. Prune old data to save space (as requested)
        two_days_ago = timezone.now() - datetime.timedelta(days=2)
        deleted_readings, _ = WaterReading.objects.filter(timestamp__lt=two_days_ago).delete()
        self.stdout.write(f'Pruned {deleted_readings} old WaterReading records.')
        
        thirty_five_days_ago = timezone.now().date() - datetime.timedelta(days=35)
        deleted_dailys, _ = DailyWaterUsage.objects.filter(date__lt=thirty_five_days_ago).delete()
        self.stdout.write(f'Pruned {deleted_dailys} old DailyWaterUsage records.')

        # 6. COMMENT ON LONG-TERM AI DATA
        # For long-term (1-3 year) analysis, we cannot rely on AI "memory".
        # The correct, space-efficient strategy is:
        # a) Create a `MonthlyWaterUsage` model.
        # b) Create another script (`aggregate_monthly_data.py`) that runs on the 1st of each month.
        # c) This script would sum all `DailyWaterUsage` data for the previous month 
        #    and save it as ONE new row in the `MonthlyWaterUsage` table.
        # d) This provides a tiny, fast dataset (e.g., 36 rows for 3 years).
        # e) We can then feed this small, aggregated dataset to the Gemini API for
        #    powerful trend analysis (e.g., "Compare this year's usage to the last 2 years.").
            
        self.stdout.write("Aggregation and pruning complete.")