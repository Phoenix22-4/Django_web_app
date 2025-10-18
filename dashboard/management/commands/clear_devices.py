from django.core.management.base import BaseCommand
from dashboard.models import Device, WaterReading, AutomationRule

class Command(BaseCommand):
    help = 'Clear all device registrations for testing automatic re-registration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all devices',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will delete ALL devices, readings, and automation rules. '
                    'Use --confirm to proceed.'
                )
            )
            return

        # Count items before deletion
        device_count = Device.objects.count()
        reading_count = WaterReading.objects.count()
        rule_count = AutomationRule.objects.count()

        # Delete all data
        WaterReading.objects.all().delete()
        AutomationRule.objects.all().delete()
        Device.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully cleared:\n'
                f'- {device_count} devices\n'
                f'- {reading_count} water readings\n'
                f'- {rule_count} automation rules\n\n'
                f'Devices will be automatically re-registered when they connect via AWS IoT.'
            )
        )
