# AquaSavvy Kenya - IoT Water Management System

## 🌊 Overview

AquaSavvy Kenya is a comprehensive IoT-driven water management system designed specifically for urban Kenyan homes and businesses. The system provides real-time remote monitoring, intelligent automation, and crucial dry-run protection to save water, energy, and money.

## ✨ Key Features

### 🎯 Phase 1: Floating AI Chat Widget
- **Amazon-style floating chat icon** fixed to bottom-right corner
- **Slide-in chat panel** with smooth animations
- **Smart routing** between public and private AI endpoints
- **Real-time AI assistance** for system queries and troubleshooting

### 🔄 Phase 2: Dynamic Architecture & Advanced Automation
- **Dynamic tank support** - automatically adapts to any number of tanks
- **JSON-based tank data** storage for maximum flexibility
- **User-defined automation rules** with custom time slots
- **4-slot automation interface** with visual rule management
- **Intelligent pump control** based on active automation rules

### 📊 Phase 3: UI Overhaul & Data Analytics
- **Icon-based navigation** with Font Awesome icons
- **Real-time analytics charts** (Pump Runtime & Power Usage)
- **Daily data aggregation** system for long-term storage
- **Custom admin analytics dashboard** with downloadable reports
- **Automated data cleanup** to optimize database performance

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
- **AWS IoT Core** - MQTT message broker
- **PostgreSQL** - User and device data
- **DynamoDB** - High-volume sensor data (future)
- **Chart.js** - Analytics visualization

## 📱 User Interface

### Dashboard Features
- **Dynamic tank visualization** with real-time water levels
- **Interactive pump controls** with status indicators
- **Automation timeslots** with 4-slot rule management
- **Real-time status messages** and system health
- **Analytics charts** for pump runtime and power usage
- **Floating AI chat** for instant assistance

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
# Dynamic tank support
class WaterReading(models.Model):
    tank_data = models.JSONField(default=list)  # [{"name": "Tank1", "level": 85}]
    
# User automation rules
class AutomationRule(models.Model):
    device = models.ForeignKey(Device)
    start_time = models.TimeField()
    end_time = models.TimeField()
    min_level = models.IntegerField()
    max_level = models.IntegerField()
    destination_tank = models.CharField(max_length=50)
    
# Daily data aggregation
class DailyWaterUsage(models.Model):
    device = models.ForeignKey(Device)
    day = models.DateField()
    total_usage_liters = models.IntegerField()
    total_power_kwh = models.FloatField()
    pump_runtime_hours = models.FloatField()
```

### WebSocket Communication
- **Real-time data updates** from ESP32 devices
- **Dynamic tank rendering** based on JSON data
- **Automation status updates** with active rule information
- **Pump control commands** sent to devices

### Data Management
- **Automatic aggregation** of daily usage statistics
- **Intelligent cleanup** of old data (48h raw, 35d daily)
- **CSV export** functionality for analytics
- **Anonymized data** for privacy compliance

## 🚀 Deployment

### Phase 1: Quick Hosting (Render)
- Initial deployment on Render for simplicity
- Managed PostgreSQL database
- Automatic HTTPS/SSL certificates

### Phase 2: Scale & Cost Optimization (AWS)
- Migration to AWS Elastic Beanstalk
- AWS S3 for static files
- Fine-grained cost control and performance tuning

### Future: Advanced Features
- Over-the-Air (OTA) updates
- SMS/Email alerting system
- Advanced analytics with machine learning

## 📊 Analytics & Monitoring

### Admin Dashboard
- **Water usage analytics** with pie and line charts
- **Power consumption tracking** by device
- **Pump runtime statistics** for efficiency analysis
- **CSV data export** for external analysis
- **Real-time device monitoring**

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
- **Data anonymization** for analytics exports

## 📞 Support & Contact

- **Email**: contact@vision072025@gmail.com
- **WhatsApp**: +254 702 715070
- **Location**: Nairobi, Kenya

## 🛠️ Development Setup

### Prerequisites
- Python 3.8+
- Django 4.0+
- PostgreSQL
- Redis (for channels)

### Installation
```bash
# Clone repository
git clone <repository-url>
cd AquaGuard_Django

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
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

## 🔮 Future Roadmap

1. **Machine Learning Integration** - Predictive maintenance
2. **Mobile App Development** - Native iOS/Android apps
3. **Multi-tenant Architecture** - Support for multiple organizations
4. **Advanced Analytics** - AI-powered insights and recommendations
5. **Integration APIs** - Third-party system integration
6. **Blockchain Integration** - Water usage verification and trading

## 📄 License

© 2025 AquaSavvy Kenya. A Production-Ready IoT Solution.

---

*Built with ❤️ for sustainable water management in Kenya*