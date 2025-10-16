from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
from dashboard.models import Device, WaterReading, DailyWaterUsage

class Command(BaseCommand):
    help = 'Aggregate daily water usage and clean up old data'

    def handle(self, *args, **options):
        # Compute previous day range in server timezone
        today = timezone.localdate()
        day = today - timedelta(days=1)
        start_dt = timezone.make_aware(timezone.datetime.combine(day, timezone.datetime.min.time()))
        end_dt = timezone.make_aware(timezone.datetime.combine(day, timezone.datetime.max.time()))

        for device in Device.objects.all():
            readings = WaterReading.objects.filter(device=device, timestamp__range=(start_dt, end_dt)).order_by('timestamp')
            if not readings.exists():
                continue
            # Simple heuristic: usage approximated by decrease in overhead (consumption)
            levels = list(readings.values_list('overhead_level', flat=True))
            total_drop = 0
            for i in range(1, len(levels)):
                diff = levels[i-1] - levels[i]
                if diff > 0:
                    total_drop += diff
            # Convert % drop to liters if calibration exists; here we store % as proxy
            DailyWaterUsage.objects.update_or_create(device=device, day=day, defaults={'total_usage_liters': total_drop})

        # Data retention
        # Delete raw readings older than 48 hours
        cutoff_raw = timezone.now() - timedelta(hours=48)
        WaterReading.objects.filter(timestamp__lt=cutoff_raw).delete()

        # Delete daily aggregates older than 35 days
        cutoff_daily = timezone.localdate() - timedelta(days=35)
        DailyWaterUsage.objects.filter(day__lt=cutoff_daily).delete()

        # NOTE FOR LONG-TERM (6-36 months) ANALYSIS WITH GEMINI:
        # - Create another model MonthlyWaterUsage(device, month(date), total_usage_liters)
        # - Run a monthly scheduled task to sum DailyWaterUsage for the month into MonthlyWaterUsage
        # - Retain MonthlyWaterUsage for years at tiny storage cost
        # - When you need AI insights, query the summarized rows and feed them to Gemini, e.g.:
        #   "Here is total water usage for the last 36 months. Analyze seasonal trends and compare this year vs previous." 

