# AquaGuard Dashboard System

## 🌊 Intelligent Water Management System

AquaGuard is a comprehensive water management system that provides real-time monitoring, automated controls, and intelligent notifications for your water tank system. Built with Django and modern web technologies, it offers a responsive dashboard with live analytics, pump control, and safety monitoring.

## ✨ Key Features

### 🎯 Real-Time Monitoring
- **Live Tank Levels**: Real-time water level monitoring with visual indicators
- **Pump Status**: Current sensor monitoring with safety controls
- **Connection Status**: WebSocket-based real-time communication
- **System Health**: Comprehensive system status monitoring

### 📱 Comprehensive Notification System
- **Tank Level Alerts**: Critical, low, and full level notifications
- **Pump Safety Alerts**: Overload, dry run, and current monitoring
- **Connection Monitoring**: Device and WebSocket failure detection
- **Security Notifications**: Password change alerts with timestamps

### 🎛️ Intelligent Controls
- **Manual Pump Control**: ON/OFF controls with safety checks
- **Automated Operation**: Auto and timeslot operation modes
- **Safety Systems**: Automatic shutdown for critical conditions
- **Source Tank Management**: Special handling for water supply tanks

### 📊 Live Analytics
- **24-Hour Water Usage**: Daily consumption tracking
- **24-Hour Pump Usage**: Daily operation hours monitoring
- **Real-Time Updates**: Live data refresh every minute
- **Historical Data**: Daily reset with data retention

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Django 4.2+
- PostgreSQL (production) / SQLite (development)
- Redis (for WebSocket support)
- Modern web browser

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd AquaGuard_Django

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run development server
python manage.py runserver
```

### Configuration
1. **Access Django Admin**: Navigate to `/admin/`
2. **Create Device**: Add your AquaGuard device
3. **Configure Tanks**: Set tank names, reading IDs, and capacities
4. **Set Source Tank**: Mark your main water supply tank
5. **Access Dashboard**: Navigate to `/dashboard/<device_id>/`

## 📚 Documentation

### User Documentation
- **[User Manual](AquaGuard_User_Manual.md)**: Complete user guide with all features
- **[Quick Reference](AquaGuard_Quick_Reference.md)**: Essential information for daily operation

### Technical Documentation
- **[Technical Documentation](AquaGuard_Technical_Documentation.md)**: System architecture and implementation details

## 🎯 System Features

### Dashboard Components

#### Left Column - Live Analytics
- **Water Usage Chart**: 24-hour water consumption tracking
- **Pump Usage Chart**: 24-hour pump operation hours
- **Mode Controls**: Auto/Timeslot operation modes
- **Timeslot Settings**: Scheduled operation controls

#### Center Column - Live Tank Status
- **Tank Displays**: Real-time tank levels with visual indicators
- **Tank Information**: Name, capacity, and current volume
- **Source Tank Indicators**: Special marking for source tanks
- **Level Percentages**: Real-time percentage and liters remaining

#### Right Column - Pump Control
- **Pump Animation**: Visual pump status with rotation animation
- **Pump Controls**: ON/OFF buttons for manual control
- **Current Monitoring**: Real-time current sensor readings
- **Status Display**: Pump state and safety information

### Notification System

#### Tank Level Notifications
- **🚨 Critical Level** (< 10%): Immediate refill required
- **⚠️ Low Level** (< 25%): Water conservation recommended
- **✅ Full Level** (≥ 95%): Optimal water storage confirmed

#### Pump Safety Notifications
- **⚠️ Pump Overload** (> 6A): Automatic safety shutdown
- **⚠️ Dry Run Detection** (< 1.5A): Prevents pump damage
- **⚠️ High Current Warning** (> 5A): Early warning system

#### Connection Monitoring
- **🔌 Connection Lost** (> 10s): Device communication failure
- **🔐 Password Changed**: Security notification with timestamp

### Safety Features
- **Automatic Shutdown**: Source tank critical, pump overload, dry run
- **Real-time Monitoring**: Continuous current and level tracking
- **Connection Monitoring**: Automatic failure detection
- **Safety Override**: Manual controls with safety checks

## 🛠️ Technology Stack

### Backend
- **Django 4.2+**: Web framework with admin interface
- **Django Channels**: WebSocket support for real-time communication
- **PostgreSQL**: Production database
- **Redis**: WebSocket channel layer

### Frontend
- **HTML5/CSS3**: Modern web standards
- **JavaScript ES6+**: Interactive dashboard functionality
- **Tailwind CSS**: Responsive design framework
- **Chart.js**: Live analytics visualization

### Communication
- **WebSocket**: Real-time bidirectional communication
- **Browser Notifications**: Native notification system
- **Firebase Cloud Messaging**: Mobile push notifications

### Deployment
- **Railway**: Cloud platform deployment
- **Docker**: Containerization support
- **WhiteNoise**: Static file serving
- **SSL/TLS**: Secure communication

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Redis (for WebSocket)
REDIS_URL=redis://localhost:6379

# Firebase Cloud Messaging
FCM_SERVER_KEY=your_fcm_server_key
FCM_SENDER_ID=your_fcm_sender_id

# Django
SECRET_KEY=your_secret_key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
```

### Tank Configuration
1. **Tank Name**: Descriptive name (e.g., "Overhead Tank")
2. **Reading ID**: Sensor data key (e.g., "overhead_level")
3. **Capacity**: Tank capacity in liters
4. **Source Tank**: Mark main water supply tank

### Notification Settings
- **Browser Permissions**: Allow notifications in browser
- **Thresholds**: Customizable alert levels
- **Delivery Methods**: Browser and mobile notifications

## 📱 Mobile Support

### Responsive Design
- **Mobile-First**: Optimized for mobile devices
- **Touch Controls**: Touch-friendly interface
- **Responsive Layout**: Adapts to screen size
- **Mobile Notifications**: Native mobile support

### Browser Compatibility
- **Chrome**: Version 80 or higher
- **Firefox**: Version 75 or higher
- **Safari**: Version 13 or higher
- **Edge**: Version 80 or higher

## 🔒 Security Features

### Authentication
- **User Authentication**: Django's built-in system
- **Device Authentication**: Device ID-based WebSocket auth
- **Session Management**: Secure session handling

### Data Protection
- **HTTPS**: SSL/TLS encryption
- **CSRF Protection**: Cross-site request forgery prevention
- **XSS Prevention**: Input sanitization and output escaping
- **SQL Injection Prevention**: Django ORM protection

### Notification Security
- **Permission-based**: User consent for notifications
- **Secure Messaging**: Encrypted notification delivery
- **Rate Limiting**: Prevent notification spam

## 🚀 Deployment

### Railway Deployment
1. **Connect Repository**: Link GitHub repository
2. **Environment Variables**: Set required variables
3. **Database**: Configure PostgreSQL
4. **Redis**: Set up Redis for WebSocket
5. **Domain**: Configure custom domain

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver

# Start WebSocket server
python manage.py runserver 0.0.0.0:8000
```

## 📊 Monitoring and Analytics

### Real-Time Metrics
- **Tank Levels**: Continuous level monitoring
- **Pump Status**: Current and status tracking
- **Connection Status**: WebSocket and device connectivity
- **System Health**: Overall system performance

### Historical Data
- **24-Hour Charts**: Daily usage patterns
- **Water Consumption**: Daily water usage tracking
- **Pump Operation**: Daily pump usage hours
- **System Events**: Notification and alert history

## 🔍 Troubleshooting

### Common Issues
- **Tanks not displaying**: Check Django admin configuration
- **Pump not responding**: Verify WebSocket connection
- **Notifications not working**: Check browser permissions
- **Connection issues**: Verify device and network status

### Support Resources
- **User Manual**: Comprehensive user guide
- **Quick Reference**: Essential daily operations
- **Technical Documentation**: System architecture details
- **Browser Console**: JavaScript error debugging

## 🤝 Contributing

### Development Setup
1. **Fork Repository**: Create your own fork
2. **Create Branch**: Feature or bugfix branch
3. **Make Changes**: Implement your changes
4. **Test Thoroughly**: Ensure all features work
5. **Submit Pull Request**: Request code review

### Code Standards
- **Python**: PEP 8 style guide
- **JavaScript**: ES6+ modern syntax
- **HTML/CSS**: Semantic markup and responsive design
- **Documentation**: Clear and comprehensive comments

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Django Community**: For the excellent web framework
- **Tailwind CSS**: For the responsive design system
- **Chart.js**: For the analytics visualization
- **Browser APIs**: For notification and WebSocket support

## 📞 Support

### Documentation
- **[User Manual](AquaGuard_User_Manual.md)**: Complete user guide
- **[Quick Reference](AquaGuard_Quick_Reference.md)**: Daily operations
- **[Technical Documentation](AquaGuard_Technical_Documentation.md)**: System details

### Getting Help
1. **Check Documentation**: Review user manual and quick reference
2. **Browser Console**: Check for JavaScript errors
3. **System Status**: Review dashboard status indicators
4. **Contact Support**: Provide system logs and error details

---

**AquaGuard Dashboard v1.5** - Intelligent Water Management System

*Built with ❤️ for efficient water management and safety*