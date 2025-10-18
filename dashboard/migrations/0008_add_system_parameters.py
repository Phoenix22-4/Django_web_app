# Generated manually for system parameters

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_update_tank_configuration'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='overload_current_amps',
            field=models.FloatField(default=15.0, help_text='Current threshold for overload detection (Amps)'),
        ),
        migrations.AddField(
            model_name='device',
            name='dry_run_current_amps',
            field=models.FloatField(default=2.0, help_text='Current threshold for dry run detection (Amps)'),
        ),
    ]
