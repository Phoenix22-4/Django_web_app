# dashboard/push_notifications.py
import json
import logging
import os
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from firebase_admin import messaging
from firebase_admin import credentials
import firebase_admin
from .models import Device, Profile

logger = logging.getLogger(__name__)

class PushNotificationService:
    def __init__(self):
        self.firebase_initialized = False
        self.initialize_firebase()

    def initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                # Try to get Firebase service account JSON from environment variable
                firebase_json = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')
                
                if not firebase_json:
                    logger.warning("Firebase credentials not configured. Missing: FIREBASE_SERVICE_ACCOUNT_JSON")
                    self.firebase_initialized = False
                    return
                
                try:
                    # Parse the JSON string
                    import json
                    firebase_config = json.loads(firebase_json)
                    
                    # Initialize Firebase Admin SDK with the service account
                    cred = credentials.Certificate(firebase_config)
                    firebase_admin.initialize_app(cred)
                    self.firebase_initialized = True
                    logger.info("Firebase Admin SDK initialized successfully")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid Firebase service account JSON: {e}")
                    self.firebase_initialized = False
                    return
                    
            else:
                self.firebase_initialized = True
                logger.info("Firebase Admin SDK already initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
            self.firebase_initialized = False

    def send_notification_to_user(self, user, title, body, data=None):
        """Send push notification to a specific user"""
        try:
            if not self.firebase_initialized:
                logger.error("Firebase not initialized")
                return False

            # Get user's FCM token (you'll need to store this in the Profile model)
            try:
                profile = user.get_profile()
                fcm_token = getattr(profile, 'fcm_token', None)
                
                if not fcm_token:
                    logger.warning(f"No FCM token found for user {user.username}")
                    return False
                
                # Create the message
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body
                    ),
                    data=data or {},
                    token=fcm_token
                )
                
                # Send the message
                response = messaging.send(message)
                logger.info(f"Successfully sent notification to {user.username}: {response}")
                return True
                
            except Exception as e:
                logger.error(f"Error sending notification to user {user.username}: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error in send_notification_to_user: {e}")
            return False

    def send_notification_to_device_owner(self, device_id, title, body, data=None):
        """Send notification to device owner"""
        try:
            device = Device.objects.get(device_id=device_id)
            if device.owner:
                return self.send_notification_to_user(device.owner, title, body, data)
            else:
                logger.warning(f"Device {device_id} has no owner")
                return False
        except Device.DoesNotExist:
            logger.error(f"Device {device_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error sending notification to device owner: {e}")
            return False

    def send_tank_level_alert(self, device_id, tank_name, level, min_level, max_level):
        """Send tank level alert"""
        try:
            if level < min_level:
                title = "Low Water Level Alert"
                body = f"Tank '{tank_name}' is at {level}% - below minimum threshold of {min_level}%"
                alert_type = "low_level"
            elif level > max_level:
                title = "High Water Level Alert"
                body = f"Tank '{tank_name}' is at {level}% - above maximum threshold of {max_level}%"
                alert_type = "high_level"
            else:
                return True  # No alert needed
            
            data = {
                "device_id": device_id,
                "tank_name": tank_name,
                "level": str(level),
                "alert_type": alert_type,
                "timestamp": datetime.now().isoformat()
            }
            
            return self.send_notification_to_device_owner(device_id, title, body, data)
            
        except Exception as e:
            logger.error(f"Error sending tank level alert: {e}")
            return False

    def send_pump_status_alert(self, device_id, pump_status, reason=None):
        """Send pump status alert"""
        try:
            if pump_status:
                title = "Pump Started"
                body = f"Pump has been turned ON for device {device_id}"
                if reason:
                    body += f" - {reason}"
            else:
                title = "Pump Stopped"
                body = f"Pump has been turned OFF for device {device_id}"
                if reason:
                    body += f" - {reason}"
            
            data = {
                "device_id": device_id,
                "pump_status": str(pump_status),
                "reason": reason or "",
                "timestamp": datetime.now().isoformat()
            }
            
            return self.send_notification_to_device_owner(device_id, title, body, data)
            
        except Exception as e:
            logger.error(f"Error sending pump status alert: {e}")
            return False

    def send_system_alert(self, device_id, alert_type, message):
        """Send system alert"""
        try:
            title = f"AquaSavvy System Alert - {alert_type.title()}"
            body = f"Device {device_id}: {message}"
            
            data = {
                "device_id": device_id,
                "alert_type": alert_type,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
            
            return self.send_notification_to_device_owner(device_id, title, body, data)
            
        except Exception as e:
            logger.error(f"Error sending system alert: {e}")
            return False

    def send_welcome_notification(self, user):
        """Send welcome notification after login"""
        try:
            title = "Welcome to AquaSavvy!"
            body = "Your water management system is now connected. You'll receive alerts about your devices."
            
            data = {
                "type": "welcome",
                "timestamp": datetime.now().isoformat()
            }
            
            return self.send_notification_to_user(user, title, body, data)
            
        except Exception as e:
            logger.error(f"Error sending welcome notification: {e}")
            return False

# Global instance
push_notification_service = PushNotificationService()
