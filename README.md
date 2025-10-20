# AquaSavvy Kenya - Advanced IoT Water Management System

## 🌊 Overview

AquaSavvy Kenya is a comprehensive IoT-driven water management system designed specifically for urban Kenyan homes and businesses. The system provides real-time remote monitoring, intelligent automation, AWS IoT integration, AI-powered assistance, and push notifications to save water, energy, and money.

## ✨ Key Features

### 🎯 Phase 1: Floating AI Chat Widget ✅ COMPLETE
- **Amazon-style floating chat icon** fixed to bottom-right corner
- **Slide-in chat panel** with smooth animations
- **Smart routing** between public and private AI endpoints
- **Real-time AI assistance** powered by Google Gemini
- **System-specific knowledge** for troubleshooting and guidance

### 🔄 Phase 2: Dynamic Architecture & Advanced Automation ✅ COMPLETE
- **Dynamic tank support** - automatically adapts to any number of tanks
- **JSON-based tank data** storage for maximum flexibility
- **User-defined automation rules** with custom time slots
- **4-slot automation interface** with visual rule management
- **Intelligent pump control** based on active automation rules
- **Real-time rule execution** with AWS IoT command delivery

### 🏗️ Phase 7: Enhanced Tank Configuration ✅ COMPLETE
- **Dynamic tank identification** using reading IDs from IoT data
- **Source tank configuration** with admin checkbox selection
- **Colorful UI design** with gradient backgrounds and animations
- **Real-time tank status** with color-coded level indicators
- **Admin panel integration** for tank name and source configuration
- **Automatic tank display** based on configured tanks only

### 📊 Phase 3: UI Overhaul & Data Analytics ✅ COMPLETE
- **Icon-based navigation** with Font Awesome icons
- **Real-time analytics charts** (Pump Runtime & Power Usage)
- **Daily data aggregation** system for long-term storage
- **Custom admin analytics dashboard** with downloadable reports
- **Automated data cleanup** to optimize database performance

### ☁️ Phase 4: AWS IoT Integration ✅ COMPLETE
- **Real-time device data reception** from AWS IoT Core
- **Device shadow management** for state synchronization
- **Automatic pump control** via AWS IoT commands
- **Manual device control** through web interface
- **Connection monitoring** with status indicators
- **Reliable command delivery** with error handling

### 📱 Phase 5: Push Notifications ✅ COMPLETE
- **Browser-based notifications** (no Firebase required)
- **Tank level alerts** for low/high water levels
- **Pump status notifications** for start/stop events
- **Solenoid valve status** notifications
- **System alerts** for connection issues and safety
- **Welcome notifications** after login
- **Test notification** functionality in dashboard

### 🤖 Phase 6: AI-Powered Assistance ✅ COMPLETE
- **Google Gemini AI** integration for intelligent responses
- **System-specific knowledge base** for AquaSavvy devices
- **Troubleshooting assistance** with contextual help
- **Maintenance recommendations** based on usage patterns
- **AWS IoT configuration guidance** for technical support

### 🔧 Phase 7: Advanced Dashboard & Solenoid Control ✅ COMPLETE
- **Modern dark theme** dashboard with advanced UI
- **Dynamic tank visualization** with smooth animations
- **Solenoid valve control** for individual tank management
- **Enhanced connection status** with blue indicators
- **Real-time charts** for water usage and pump runtime
- **Mode selection** (Auto/Timeslot) with visual feedback
- **Safety alerts** for source tank low and dry run detection

## 🏗️ System Architecture

### Hardware Components
- **ESP32 Microcontroller** - Wi-Fi connectivity and processing
- **JSN-SR04T Ultrasonic Sensor** - Water level measurement
- **ACS712 Current Sensor** - Pump status monitoring
- **Solid State Relay (SSR-40DA)** - Pump control
- **Hybrid power system** with battery backup

### Software Stack
- **Django Web Application** - User interface and API
- **Django Channels** - WebSocket real-time communication
- **AWS IoT Core** - MQTT message broker and device management
- **PostgreSQL** - User and device data storage
- **Firebase Admin SDK** - Push notification service
- **Google Gemini AI** - Intelligent assistance
- **Chart.js** - Analytics visualization
- **Boto3** - AWS SDK for Python

## 📱 User Interface

### Dashboard Features
- **Advanced dark theme** with modern UI design
- **Dynamic tank visualization** with smooth animations and real-time water levels
- **Interactive pump controls** with AWS IoT command delivery
- **Solenoid valve control** for individual tank management (up to 4 valves)
- **Automation timeslots** with 4-slot rule management
- **Real-time status messages** and system health monitoring
- **Live analytics charts** for water usage and pump runtime
- **Mode selection** (Auto/Timeslot) with visual feedback
- **Safety alerts** for source tank low and dry run detection
- **Floating AI chat** for instant assistance
- **Push notification controls** with test functionality
- **Enhanced connection status** with blue indicators for better visibility

### Public Homepage
- **Professional landing page** with system overview
- **Interactive architecture diagram** with hover details
- **Economic impact analysis** with cost breakdowns
- **AI-powered insights** for market viability and safety
- **About Us section** with team information
- **Production roadmap** and deployment strategy

## 🔧 Technical Implementation

### Models
```python
# Dynamic tank support with AWS IoT integration
class WaterReading(models.Model):
    tank_data = models.JSONField(default=list)  # [{"name": "Tank1", "level": 85}]
    pump_status = models.BooleanField(default=False)
    pump_current_amps = models.FloatField(default=0.0)
    
# User automation rules with AWS IoT control
class AutomationRule(models.Model):
    device = models.ForeignKey(Device, related_name='rules')
    start_time = models.TimeField()
    end_time = models.TimeField()
    min_level = models.IntegerField()
    max_level = models.IntegerField()
    monitor_tank_name = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)
    
# Daily data aggregation with power tracking
class DailyWaterUsage(models.Model):
    device = models.ForeignKey(Device, related_name='daily_usage')
    date = models.DateField()
    total_user_water_liters = models.FloatField(default=0.0)
    total_stored_water_liters = models.FloatField(default=0.0)
    total_power_kwh = models.FloatField(default=0.0)

# Push notification support
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fcm_token = models.TextField(blank=True, null=True)
    push_notifications_enabled = models.BooleanField(default=True)
    last_notification_sent = models.DateTimeField(blank=True, null=True)

# Solenoid valve configuration
class Device(models.Model):
    # ... existing fields ...
    solenoid_1_reading_id = models.CharField(max_length=100, blank=True, null=True)
    solenoid_1_name = models.CharField(max_length=100, blank=True, null=True)
    solenoid_2_reading_id = models.CharField(max_length=100, blank=True, null=True)
    solenoid_2_name = models.CharField(max_length=100, blank=True, null=True)
    solenoid_3_reading_id = models.CharField(max_length=100, blank=True, null=True)
    solenoid_3_name = models.CharField(max_length=100, blank=True, null=True)
    solenoid_4_reading_id = models.CharField(max_length=100, blank=True, null=True)
    solenoid_4_name = models.CharField(max_length=100, blank=True, null=True)
```

### AWS IoT Integration
```python
# Real-time device data processing
class AWSIoTManager:
    def process_device_data(self, device_id, data):
        # Process incoming device data from AWS IoT
        # Create water readings
        # Check automation rules
        # Send pump commands if needed
        
    def send_pump_command(self, device_id, pump_on):
        # Send pump control command via AWS IoT
        # Update device shadow
        # Handle command delivery
        
    def get_device_shadow(self, device_id):
        # Retrieve device state from AWS IoT
        # Return current device status
```

### Push Notification System
```python
# Firebase push notification service
class PushNotificationService:
    def send_tank_level_alert(self, device_id, tank_name, level, min_level, max_level):
        # Send tank level alerts to device owners
        
    def send_pump_status_alert(self, device_id, pump_status, reason=None):
        # Send pump status notifications
        
    def send_welcome_notification(self, user):
        # Send welcome message after login
```

### WebSocket Communication
- **Real-time data updates** from ESP32 devices via AWS IoT
- **Dynamic tank rendering** based on JSON data
- **Automation status updates** with active rule information
- **Pump control commands** sent to devices via AWS IoT
- **Push notification triggers** for important events

### Data Management
- **Automatic aggregation** of daily usage statistics
- **Intelligent cleanup** of old data (48h raw, 35d daily)
- **CSV export** functionality for analytics
- **Anonymized data** for privacy compliance
- **AWS IoT data processing** with real-time updates

## 🚀 Deployment

### Phase 1: Quick Hosting (Render/Railway)
- Initial deployment on Railway for simplicity
- Managed PostgreSQL database
- Automatic HTTPS/SSL certificates
- Environment variable configuration

### Phase 2: Scale & Cost Optimization (AWS)
- Migration to AWS Elastic Beanstalk
- AWS S3 for static files
- AWS IoT Core for device management
- Fine-grained cost control and performance tuning

### Future: Advanced Features
- Over-the-Air (OTA) updates via AWS IoT
- SMS/Email alerting system
- Advanced analytics with machine learning
- Multi-tenant architecture

## 📊 Analytics & Monitoring

### Admin Dashboard
- **Water usage analytics** with pie and line charts
- **Power consumption tracking** by device
- **Pump runtime statistics** for efficiency analysis
- **CSV data export** for external analysis
- **Real-time device monitoring** via AWS IoT
- **Push notification management** and testing

### Data Aggregation
```bash
# Run daily aggregation (cron job)
python manage.py aggregate_daily_data

# Dry run to see what would be processed
python manage.py aggregate_daily_data --dry-run
```

## 🔒 Security Features

- **CSRF protection** for all forms and API endpoints
- **User authentication** with device ownership validation
- **WebSocket security** with user ownership checks
- **AWS IoT Core** with certificate-based authentication
- **Firebase security rules** for push notifications
- **Data anonymization** for analytics exports
- **Environment variable protection** for API keys

## 📞 Support & Contact

- **Email**: contact@vision072025@gmail.com
- **WhatsApp**: +254 702 715070
- **Location**: Nairobi, Kenya
- **AI Assistant**: Available 24/7 in the chat widget

## 🛠️ Development Setup

### Prerequisites
- Python 3.8+
- Django 4.0+
- PostgreSQL
- Redis (for channels)
- AWS Account (for IoT Core)
- Firebase Project (for push notifications)
- Google Gemini API Key

### Installation
```bash
# Clone repository
git clone <repository-url>
cd AquaGuard_Django

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run development server
python manage.py runserver
```

### Environment Variables Required
```bash
# Django Settings
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# AWS IoT Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
AWS_IOT_ENDPOINT=your-iot-endpoint.amazonaws.com

# Firebase Configuration
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nyour-private-key\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com

# Gemini AI Configuration
GEMINI_API_KEY=your-gemini-api-key
```

### Management Commands
```bash
# Aggregate daily data
python manage.py aggregate_daily_data

# Check device connectivity
python manage.py check_connectivity
```

## 📈 Performance Optimizations

- **Database indexing** on frequently queried fields
- **Automatic data cleanup** to maintain performance
- **WebSocket connection pooling** for scalability
- **Static file optimization** with CDN support
- **Chart.js lazy loading** for faster page loads
- **AWS IoT connection pooling** for device management
- **Firebase notification batching** for efficiency

## 🔮 Future Roadmap

1. **Machine Learning Integration** - Predictive maintenance with AWS SageMaker
2. **Mobile App Development** - Native iOS/Android apps with push notifications
3. **Multi-tenant Architecture** - Support for multiple organizations
4. **Advanced Analytics** - AI-powered insights and recommendations
5. **Integration APIs** - Third-party system integration
6. **Blockchain Integration** - Water usage verification and trading
7. **Edge Computing** - Local processing with AWS Greengrass
8. **Voice Control** - Amazon Alexa/Google Assistant integration

## 📄 License

© 2025 AquaSavvy Kenya. A Production-Ready IoT Solution.

---

*Built with ❤️ for sustainable water management in Kenya*