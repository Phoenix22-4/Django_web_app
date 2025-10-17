# dashboard/aws_iot_integration.py
import json
import logging
import os
from datetime import datetime
from django.conf import settings
from .models import Device, WaterReading, AutomationRule
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class AWSIoTManager:
    def __init__(self):
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        self.iot_endpoint = os.getenv('AWS_IOT_ENDPOINT')
        
        if not all([self.aws_access_key, self.aws_secret_key, self.iot_endpoint]):
            logger.warning("AWS IoT credentials not configured")
            return
            
        try:
            self.iot_client = boto3.client(
                'iot-data',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.aws_region
            )
            self.iot_core_client = boto3.client(
                'iot',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.aws_region
            )
        except Exception as e:
            logger.error(f"Failed to initialize AWS IoT client: {e}")
            self.iot_client = None
            self.iot_core_client = None

    def process_device_data(self, device_id, data):
        """Process incoming device data from AWS IoT"""
        try:
            # Get or create device
            device, created = Device.objects.get_or_create(
                device_id=device_id,
                defaults={'name': f'AquaGuard Device {device_id}'}
            )
            
            # Parse the incoming data
            if isinstance(data, str):
                data = json.loads(data)
            
            # Create water reading
            reading = WaterReading.objects.create(
                device=device,
                pump_status=data.get('pump_status', False),
                pump_current_amps=data.get('pump_current_amps', 0.0),
                tank_data=data.get('tank_data', [])
            )
            
            # Check automation rules
            self.check_automation_rules(device, reading)
            
            logger.info(f"Processed data for device {device_id}: {data}")
            return reading
            
        except Exception as e:
            logger.error(f"Error processing device data for {device_id}: {e}")
            return None

    def check_automation_rules(self, device, reading):
        """Check and execute automation rules"""
        try:
            current_time = datetime.now().time()
            active_rules = device.rules.filter(enabled=True)
            
            for rule in active_rules:
                # Check if current time is within rule time range
                if rule.start_time <= current_time <= rule.end_time:
                    # Find the tank to monitor
                    tank_data = reading.tank_data
                    target_tank = None
                    
                    for tank in tank_data:
                        if tank.get('name') == rule.monitor_tank_name:
                            target_tank = tank
                            break
                    
                    if target_tank:
                        tank_level = target_tank.get('level', 0)
                        
                        # Check if pump should be turned on/off
                        if tank_level < rule.min_level and not reading.pump_status:
                            # Turn pump ON
                            self.send_pump_command(device.device_id, True)
                            logger.info(f"Automation: Turning pump ON for {device.device_id} - tank level {tank_level}% < {rule.min_level}%")
                            
                        elif tank_level > rule.max_level and reading.pump_status:
                            # Turn pump OFF
                            self.send_pump_command(device.device_id, False)
                            logger.info(f"Automation: Turning pump OFF for {device.device_id} - tank level {tank_level}% > {rule.max_level}%")
                            
        except Exception as e:
            logger.error(f"Error checking automation rules for {device.device_id}: {e}")

    def send_pump_command(self, device_id, pump_on):
        """Send pump control command to device via AWS IoT"""
        try:
            if not self.iot_client:
                logger.error("AWS IoT client not initialized")
                return False
                
            topic = f"devices/{device_id}/commands"
            command = {
                "command": "pump_control",
                "pump_on": pump_on,
                "timestamp": datetime.now().isoformat(),
                "source": "automation"
            }
            
            response = self.iot_client.publish(
                topic=topic,
                qos=1,
                payload=json.dumps(command)
            )
            
            logger.info(f"Sent pump command to {device_id}: {command}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending pump command to {device_id}: {e}")
            return False

    def send_manual_command(self, device_id, command_type, value=None):
        """Send manual command to device"""
        try:
            if not self.iot_client:
                logger.error("AWS IoT client not initialized")
                return False
                
            topic = f"devices/{device_id}/commands"
            command = {
                "command": command_type,
                "value": value,
                "timestamp": datetime.now().isoformat(),
                "source": "manual"
            }
            
            response = self.iot_client.publish(
                topic=topic,
                qos=1,
                payload=json.dumps(command)
            )
            
            logger.info(f"Sent manual command to {device_id}: {command}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending manual command to {device_id}: {e}")
            return False

    def get_device_shadow(self, device_id):
        """Get device shadow from AWS IoT"""
        try:
            if not self.iot_client:
                return None
                
            response = self.iot_client.get_thing_shadow(
                thingName=device_id
            )
            
            shadow_data = json.loads(response['payload'].read())
            return shadow_data.get('state', {}).get('reported', {})
            
        except Exception as e:
            logger.error(f"Error getting device shadow for {device_id}: {e}")
            return None

    def update_device_shadow(self, device_id, desired_state):
        """Update device shadow desired state"""
        try:
            if not self.iot_client:
                return False
                
            shadow_update = {
                "state": {
                    "desired": desired_state
                }
            }
            
            response = self.iot_client.update_thing_shadow(
                thingName=device_id,
                payload=json.dumps(shadow_update)
            )
            
            logger.info(f"Updated device shadow for {device_id}: {desired_state}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating device shadow for {device_id}: {e}")
            return False

# Global instance
aws_iot_manager = AWSIoTManager()
