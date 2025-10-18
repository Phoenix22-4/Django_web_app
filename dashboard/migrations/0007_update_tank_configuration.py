# Generated manually for updated tank configuration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_add_tank_name_fields'),
    ]

    operations = [
        # Add reading_id fields
        migrations.AddField(
            model_name='device',
            name='tank_1_reading_id',
            field=models.CharField(blank=True, help_text='Reading ID for Tank 1 (auto-detected from IoT data)', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='tank_2_reading_id',
            field=models.CharField(blank=True, help_text='Reading ID for Tank 2 (auto-detected from IoT data)', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='tank_3_reading_id',
            field=models.CharField(blank=True, help_text='Reading ID for Tank 3 (auto-detected from IoT data)', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='tank_4_reading_id',
            field=models.CharField(blank=True, help_text='Reading ID for Tank 4 (auto-detected from IoT data)', max_length=100, null=True),
        ),
        
        # Update WaterReading model
        migrations.RemoveField(
            model_name='waterreading',
            name='pump_current_amps',
        ),
        migrations.RemoveField(
            model_name='waterreading',
            name='pump_status',
        ),
        migrations.RemoveField(
            model_name='waterreading',
            name='tank_data',
        ),
        migrations.AddField(
            model_name='waterreading',
            name='system_data',
            field=models.JSONField(default=dict),
        ),
    ]
