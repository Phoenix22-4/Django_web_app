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
        # Don't initialize immediately to avoid import errors
        # Initialize when first needed

    def initialize_firebase(self):
        """Initialize Firebase Admin SDK with comprehensive logging"""
        try:
            print("🔧 FIREBASE INIT: Starting Firebase Admin SDK initialization...")
            
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                print("🔧 FIREBASE INIT: No existing Firebase apps found, proceeding with initialization...")
                
                # Try to get Firebase service account JSON from environment variable
                firebase_json = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')
                
                if not firebase_json:
                    print("❌ FIREBASE INIT: FIREBASE_SERVICE_ACCOUNT_JSON environment variable not found")
                    logger.warning("Firebase credentials not configured. Missing: FIREBASE_SERVICE_ACCOUNT_JSON")
                    self.firebase_initialized = False
                    return
                
                print(f"✅ FIREBASE INIT: Found FIREBASE_SERVICE_ACCOUNT_JSON (length: {len(firebase_json)})")
                
                try:
                    # Parse the JSON string
                    import json
                    print("🔧 FIREBASE INIT: Parsing JSON configuration...")
                    firebase_config = json.loads(firebase_json)
                    print("✅ FIREBASE INIT: JSON parsed successfully")
                    
                    # Fix private key format - replace literal \n with actual newlines
                    if 'private_key' in firebase_config and isinstance(firebase_config['private_key'], str):
                        print("🔧 FIREBASE INIT: Processing private key format...")
                        original_key = firebase_config['private_key']
                        firebase_config['private_key'] = firebase_config['private_key'].replace('\\n', '\n')
                        
                        # Ensure proper PEM format
                        if not firebase_config['private_key'].endswith('-----END PRIVATE KEY-----\n'):
                            if firebase_config['private_key'].endswith('-----END PRIVATE KEY-----'):
                                firebase_config['private_key'] += '\n'
                            else:
                                firebase_config['private_key'] += '\n-----END PRIVATE KEY-----\n'
                        
                        print("✅ FIREBASE INIT: Private key format corrected")
                    
                    # Validate required fields
                    required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
                    missing_fields = [field for field in required_fields if field not in firebase_config]
                    if missing_fields:
                        print(f"❌ FIREBASE INIT: Missing required fields: {missing_fields}")
                        raise ValueError(f"Missing required Firebase fields: {missing_fields}")
                    
                    print(f"✅ FIREBASE INIT: All required fields present. Project ID: {firebase_config.get('project_id', 'N/A')}")
                    
                    # Initialize Firebase Admin SDK with the service account
                    print("🔧 FIREBASE INIT: Creating credentials object...")
                    cred = credentials.Certificate(firebase_config)
                    print("✅ FIREBASE INIT: Credentials object created successfully")
                    
                    print("🔧 FIREBASE INIT: Initializing Firebase app...")
                    firebase_admin.initialize_app(cred)
                    print("✅ FIREBASE INIT: Firebase Admin SDK initialized successfully")
                    
                    self.firebase_initialized = True
                    logger.info("Firebase Admin SDK initialized successfully")
                    
                except json.JSONDecodeError as e:
                    print(f"❌ FIREBASE INIT: Invalid JSON in FIREBASE_SERVICE_ACCOUNT_JSON: {e}")
                    logger.error(f"Invalid Firebase service account JSON: {e}")
                    self.firebase_initialized = False
                    return
                except Exception as e:
                    print(f"❌ FIREBASE INIT: Failed to initialize Firebase credentials: {e}")
                    logger.error(f"Failed to initialize Firebase credentials: {e}")
                    self.firebase_initialized = False
                    return
                    
            else:
                print("✅ FIREBASE INIT: Firebase Admin SDK already initialized")
                self.firebase_initialized = True
                logger.info("Firebase Admin SDK already initialized")
                
        except Exception as e:
            print(f"❌ FIREBASE INIT: Critical error in Firebase initialization: {e}")
            logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
            self.firebase_initialized = False

    def send_notification_to_user(self, user, title, body, data=None):
        """Send push notification to a specific user"""
        try:
            # Initialize Firebase if not already done
            if not self.firebase_initialized:
                self.initialize_firebase()
                
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
