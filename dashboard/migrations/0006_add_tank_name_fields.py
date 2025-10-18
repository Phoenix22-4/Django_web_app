# Generated manually for tank name fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_profile_push_notifications'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='tank_1_name',
            field=models.CharField(blank=True, help_text='Name for Tank 1 (auto-detected from IoT data)', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='tank_2_name',
            field=models.CharField(blank=True, help_text='Name for Tank 2 (auto-detected from IoT data)', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='tank_3_name',
            field=models.CharField(blank=True, help_text='Name for Tank 3 (auto-detected from IoT data)', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='tank_4_name',
            field=models.CharField(blank=True, help_text='Name for Tank 4 (auto-detected from IoT data)', max_length=100, null=True),
        ),
    ]
