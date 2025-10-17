# AquaSavvy Configuration Guide

## Environment Variables Required

### Django Settings
- `SECRET_KEY`: Django secret key for security
- `DEBUG`: Set to True for development, False for production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

### Database
- `DATABASE_URL`: Database connection string (e.g., sqlite:///db.sqlite3 or postgresql://user:pass@host:port/db)

### AWS IoT Configuration
- `AWS_ACCESS_KEY_ID`: Your AWS access key ID
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key
- `AWS_REGION`: AWS region (e.g., us-east-1)
- `AWS_IOT_ENDPOINT`: Your AWS IoT endpoint URL

### Firebase Configuration
- `FIREBASE_PROJECT_ID`: Your Firebase project ID
- `FIREBASE_PRIVATE_KEY_ID`: Firebase private key ID
- `FIREBASE_PRIVATE_KEY`: Firebase private key (with newlines)
- `FIREBASE_CLIENT_EMAIL`: Firebase service account email
- `FIREBASE_CLIENT_ID`: Firebase client ID
- `FIREBASE_CLIENT_X509_CERT_URL`: Firebase certificate URL

### Gemini AI Configuration
- `GEMINI_API_KEY`: Your Google Gemini API key

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**
   Create a `.env` file with the variables above, or set them in your deployment environment.

3. **Run Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

5. **Collect Static Files**
   ```bash
   python manage.py collectstatic
   ```

6. **Start Server**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Device Control
- `POST /api/pump_control/` - Manual pump control
- `POST /api/device_command/` - Send general device commands
- `GET /api/device_data/<device_id>/` - Get device data and readings

### AWS IoT Integration
- `POST /api/iot_data/` - Receive device data from AWS IoT

### Automation Rules
- `POST /api/save_rule/` - Create/update automation rules
- `POST /api/delete_rule/` - Delete automation rules

### Push Notifications
- `POST /api/register_fcm_token/` - Register FCM token
- `POST /api/test_notification/` - Send test notification

### AI Chat
- `POST /api/ai_chat/` - AI chat with Gemini

## Device Data Format

### Incoming Device Data (AWS IoT)
```json
{
    "device_id": "AquaGuard_Device_01",
    "pump_status": true,
    "pump_current_amps": 2.5,
    "tank_data": [
        {
            "name": "Overhead",
            "level": 75
        },
        {
            "name": "Underground",
            "level": 45
        }
    ]
}
```

### Pump Control Command
```json
{
    "device_id": "AquaGuard_Device_01",
    "pump_on": true
}
```

### Automation Rule
```json
{
    "device_id": "AquaGuard_Device_01",
    "name": "Morning Fill",
    "start_time": "06:00:00",
    "end_time": "08:00:00",
    "monitor_tank_name": "Overhead",
    "min_level": 20,
    "max_level": 95,
    "enabled": true
}
```

## WebSocket Events

### Device Data Update
```json
{
    "type": "device_data",
    "data": {
        "device_id": "AquaGuard_Device_01",
        "pump_status": true,
        "tank_data": [...]
    }
}
```

### Pump Status Change
```json
{
    "type": "pump_status",
    "pump_status": true,
    "device_id": "AquaGuard_Device_01"
}
```

## Troubleshooting

### Common Issues

1. **AttributeError: 'Device' object has no attribute 'automation_rules'**
   - Fixed: Changed to use `device.rules.all()` instead of `device.automation_rules.all()`

2. **Missing team member images (404 errors)**
   - Fixed: Created placeholder SVG images for all team members

3. **Missing firebase-messaging-sw.js**
   - Fixed: Copied service worker to root directory

4. **AI Chat API errors**
   - Fixed: Added proper error handling and fallback responses

5. **AWS IoT integration**
   - Added: Complete AWS IoT integration with device shadow support

6. **Push notifications**
   - Added: Firebase push notification system with FCM token management

### Logs
Check the application logs for detailed error information:
- Django logs: `python manage.py runserver` output
- AWS IoT logs: Check CloudWatch logs
- Firebase logs: Check Firebase console

### Testing
- Test device control: Use the manual pump buttons
- Test automation: Create automation rules and monitor execution
- Test notifications: Use the test notification button
- Test AI chat: Send messages through the chat interface
