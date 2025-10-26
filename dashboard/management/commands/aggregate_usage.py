from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
from dashboard.models import Device, WaterReading, DailyWaterUsage

class Command(BaseCommand):
    help = 'Aggregate daily water usage, power consumption, and clean up old data'

    def handle(self, *args, **options):
        # Compute previous day range in server timezone
        today = timezone.localdate()
        day = today - timedelta(days=1)
        start_dt = timezone.make_aware(timezone.datetime.combine(day, timezone.datetime.min.time()))
        end_dt = timezone.make_aware(timezone.datetime.combine(day, timezone.datetime.max.time()))

        self.stdout.write(self.style.SUCCESS(f"Aggregating data for {day}"))

        for device in Device.objects.all():
            readings = WaterReading.objects.filter(device=device, timestamp__range=(start_dt, end_dt)).order_by('timestamp')
            if not readings.exists():
                self.stdout.write(self.style.WARNING(f"No readings for device {device.device_id} on {day}"))
                continue
            
            # Calculate water usage (sum drops across all tanks)
            total_drop = 0
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
                        total_drop += diff
            
            # Calculate stored water (sum refills for source tanks)
            total_stored = 0
            for tank, levels in all_levels.items():
                if len(levels) > 1:
                    total_stored += levels[-1] - levels[0]
            
            # Calculate pump runtime and power consumption
            pump_on_readings = [r for r in readings if r.system_data.get('pump_status')]
            pump_on_count = len(pump_on_readings)
            total_readings = len(readings)
            
            # Estimate runtime hours (assuming readings are evenly spaced)
            reading_interval_seconds = (end_dt - start_dt).total_seconds() / max(total_readings, 1)
            pump_runtime_hours = (pump_on_count * reading_interval_seconds) / 3600
            
            # Calculate average current when pump was on
            if pump_on_readings:
                avg_current = sum([r.system_data.get('pump_current', 0) for r in pump_on_readings]) / len(pump_on_readings)
            else:
                avg_current = 0.0
            
            # Power calculation: kWh = (runtime_hours * avg_current * voltage) / 1000
            voltage = 240
            total_power_kwh = (pump_runtime_hours * avg_current * voltage) / 1000
            
            # Calculate peak hours (hours with most pump activity)
            peak_hours = []
            if pump_on_readings:
                hour_counts = {}
                for r in pump_on_readings:
                    hour = r.timestamp.hour
                    hour_counts[hour] = hour_counts.get(hour, 0) + 1
                sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
                peak_hours = [h for h, c in sorted_hours[:3]]  # Top 3 peak hours
            
            # Save aggregated data
            DailyWaterUsage.objects.update_or_create(
                device=device, 
                date=day, 
                defaults={
                    'total_user_water_liters': int(total_drop),
                    'total_stored_water_liters': int(total_stored),
                    'total_power_kwh': round(total_power_kwh, 3),
                    'total_pump_runtime_hours': round(pump_runtime_hours, 2)
                }
            )
            
            self.stdout.write(self.style.SUCCESS(
                f"✓ {device.device_id}: {total_drop}L used, {total_stored}L stored, "
                f"{pump_runtime_hours:.1f}h runtime, {total_power_kwh:.2f} kWh"
            ))

        # Data retention
        # Delete raw readings older than 48 hours
        cutoff_raw = timezone.now() - timedelta(hours=48)
        deleted_readings = WaterReading.objects.filter(timestamp__lt=cutoff_raw).count()
        WaterReading.objects.filter(timestamp__lt=cutoff_raw).delete()
        self.stdout.write(self.style.WARNING(f"Deleted {deleted_readings} old readings (>48h)"))

        # Delete daily aggregates older than 35 days
        cutoff_daily = timezone.localdate() - timedelta(days=35)
        deleted_daily = DailyWaterUsage.objects.filter(date__lt=cutoff_daily).count()
        DailyWaterUsage.objects.filter(date__lt=cutoff_daily).delete()
        self.stdout.write(self.style.WARNING(f"Deleted {deleted_daily} old daily summaries (>35d)"))

        # ===================================================================================
        # NOTE FOR LONG-TERM (6-36 months) ANALYSIS WITH GEMINI:
        # ===================================================================================
        # For analysis spanning 6 months to 3 years, follow this SPACE-EFFICIENT strategy:
        #
        # 1. CREATE A MONTHLY SUMMARY MODEL:
        #    class MonthlyWaterUsage(models.Model):
        #        device = models.ForeignKey(Device, on_delete=models.CASCADE)
        #        month = models.DateField()  # Store first day of month
        #        total_usage_liters = models.IntegerField()
        #        total_power_kwh = models.FloatField()
        #        # ... other fields as needed
        #
        # 2. CREATE A MONTHLY AGGREGATION COMMAND:
        #    Run this command on the 1st of each month:
        #    - Query all DailyWaterUsage for the previous month
        #    - Sum the totals for each device
        #    - Create one MonthlyWaterUsage entry per device
        #    - This reduces 30 days of data to 1 row (97% storage reduction!)
        #
        # 3. LONG-TERM RETENTION:
        #    - Keep DailyWaterUsage for 35 days (detailed recent data)
        #    - Keep MonthlyWaterUsage for 3+ years (tiny storage cost)
        #    - Optional: Create YearlyWaterUsage for 10+ year trends
        #
        # 4. AI ANALYSIS WITH GEMINI:
        #    When you need AI insights, query the summarized database:
        #    
        #    monthly_data = MonthlyWaterUsage.objects.filter(
        #        device__owner__isnull=False,
        #        month__gte=three_years_ago
        #    ).values('month').annotate(total=Sum('total_usage_liters'))
        #    
        #    Then feed this to Gemini API:
        #    prompt = f"""
        #    Here is the total water usage for Nairobi for the last 36 months:
        #    {json.dumps(list(monthly_data))}
        #    
        #    Analyze:
        #    1. Seasonal trends (rainy vs dry seasons)
        #    2. Year-over-year comparison (2023 vs 2024 vs 2025)
        #    3. Anomalies or unusual patterns
        #    4. Recommendations for urban water planning
        #    """
        #    
        #    This approach:
        #    - Stores the data in the database (not in AI "memory")
        #    - Uses minimal storage (36 rows for 3 years of monthly data)
        #    - Provides the AI with structured context for analysis
        #    - Allows you to sell actionable insights to water companies
        # ===================================================================================

        self.stdout.write(self.style.SUCCESS("Daily aggregation complete!")) 

