# Generated manually for source tank configuration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0009_add_solenoid_valve_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='tank_1_is_source',
            field=models.BooleanField(default=False, help_text='Check if Tank 1 is the source tank (water supply)'),
        ),
        migrations.AddField(
            model_name='device',
            name='tank_2_is_source',
            field=models.BooleanField(default=False, help_text='Check if Tank 2 is the source tank (water supply)'),
        ),
        migrations.AddField(
            model_name='device',
            name='tank_3_is_source',
            field=models.BooleanField(default=False, help_text='Check if Tank 3 is the source tank (water supply)'),
        ),
        migrations.AddField(
            model_name='device',
            name='tank_4_is_source',
            field=models.BooleanField(default=False, help_text='Check if Tank 4 is the source tank (water supply)'),
        ),
    ]
