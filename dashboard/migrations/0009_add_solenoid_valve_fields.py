# Generated manually for solenoid valve fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0008_add_system_parameters'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='solenoid_1_reading_id',
            field=models.CharField(blank=True, help_text='Reading ID for Solenoid Valve 1 (auto-detected from IoT data)', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='solenoid_1_name',
            field=models.CharField(blank=True, help_text='Name for Solenoid Valve 1 (enter only if reading_id exists)', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='solenoid_2_reading_id',
            field=models.CharField(blank=True, help_text='Reading ID for Solenoid Valve 2 (auto-detected from IoT data)', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='solenoid_2_name',
            field=models.CharField(blank=True, help_text='Name for Solenoid Valve 2 (enter only if reading_id exists)', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='solenoid_3_reading_id',
            field=models.CharField(blank=True, help_text='Reading ID for Solenoid Valve 3 (auto-detected from IoT data)', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='solenoid_3_name',
            field=models.CharField(blank=True, help_text='Name for Solenoid Valve 3 (enter only if reading_id exists)', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='solenoid_4_reading_id',
            field=models.CharField(blank=True, help_text='Reading ID for Solenoid Valve 4 (auto-detected from IoT data)', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='solenoid_4_name',
            field=models.CharField(blank=True, help_text='Name for Solenoid Valve 4 (enter only if reading_id exists)', max_length=100, null=True),
        ),
    ]
