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
                pump_on_readings = [r for r in readings if r.system_data.get('pump_status')]
                # Assuming 1 reading every 5 seconds (12 readings per minute)
                total_runtime_minutes = len(pump_on_readings) / 12.0 
                
                if total_runtime_minutes > 0:
                    average_current = sum([r.system_data.get('pump_current', 0) for r in pump_on_readings]) / len(pump_on_readings)
                    if average_current is None: average_current = 0.0
                    
                    # P = I * V. Using 240V for Kenya.
                    # kWh = (Amps * Volts * Hours) / 1000
                    total_kwh = (average_current * 240 * (total_runtime_minutes / 60.0)) / 1000
                else:
                    total_kwh = 0.0

            # 3. Calculate Water Usage (sum drops across all tanks)
            total_user_liters = 0
            total_stored_liters = 0
            all_levels = {}
            for r in readings:
                if r.system_data:
                    for key, value in r.system_data.items():
                        if key.endswith('_level'):
                            tank_key = key.replace('_level', '')
                            if tank_key not in all_levels:
                                all_levels[tank_key] = []
                            all_levels[tank_key].append(value)
            
            for tank, levels in all_levels.items():
                for i in range(1, len(levels)):
                    diff = levels[i-1] - levels[i]
                    if diff > 0:
                        total_user_liters += diff
            
            for tank, levels in all_levels.items():
                if len(levels) > 1:
                    total_stored_liters += levels[-1] - levels[0]

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