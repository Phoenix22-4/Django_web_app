# Generated migration for Profile model updates
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_alter_automationrule_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='fcm_token',
            field=models.TextField(blank=True, help_text='Firebase Cloud Messaging token for push notifications', null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='push_notifications_enabled',
            field=models.BooleanField(default=True, help_text='Enable/disable push notifications'),
        ),
        migrations.AddField(
            model_name='profile',
            name='last_notification_sent',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
