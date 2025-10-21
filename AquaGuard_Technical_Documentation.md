# AquaGuard System - Technical Documentation

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Notification System Implementation](#notification-system-implementation)
3. [WebSocket Communication](#websocket-communication)
4. [Database Schema](#database-schema)
5. [API Endpoints](#api-endpoints)
6. [Configuration Management](#configuration-management)
7. [Deployment Guide](#deployment-guide)
8. [Monitoring and Logging](#monitoring-and-logging)

---

## System Architecture

### Overview
AquaGuard is a Django-based web application with real-time WebSocket communication, providing water tank monitoring, pump control, and comprehensive notification systems.

### Technology Stack
- **Backend**: Django 4.2+ with Channels for WebSocket support
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Tailwind CSS
- **Real-time Communication**: WebSocket via Django Channels
- **Database**: PostgreSQL (production) / SQLite (development)
- **Notification System**: Browser Notifications API + Firebase Cloud Messaging
- **Deployment**: Railway (cloud platform)

### Component Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │◄──►│   Django App    │◄──►│   Database      │
│   (Dashboard)   │    │   (Backend)     │    │   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │              ┌─────────────────┐
         │              │   WebSocket     │
         └─────────────►│   (Channels)    │
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │   IoT Device    │
                        │   (Hardware)    │
                        └─────────────────┘
```

---

## Notification System Implementation

### Notification Types and Triggers

#### Tank Level Notifications
```javascript
// Source Tank Notifications
if (isSource) {
    if (level < 10) {
        sendNotification('🚨 AquaGuard Alert - Source Tank Critical', 
                        `${tankName} is critically low at ${level}%! Please refill immediately.`);
    } else if (level < 25) {
        sendNotification('⚠️ AquaGuard Alert - Source Tank Low', 
                        `${tankName} is running low at ${level}%. Use water sparingly.`);
    } else if (level >= 95) {
        sendNotification('✅ AquaGuard Info - Source Tank Full', 
                        `${tankName} is full at ${level}%. Water level is optimal.`);
    }
}

// Secondary Tank Notifications
else {
    if (level < 15) {
        sendNotification('🚨 AquaGuard Alert - Tank Minimum', 
                        `${tankName} is at minimum level (${level}%). Please refill soon.`);
    } else if (level >= 95) {
        sendNotification('✅ AquaGuard Info - Tank Full', 
                        `${tankName} is full at ${level}%. Water level is optimal.`);
    }
}
```

#### Pump Safety Notifications
```javascript
// Pump Current Monitoring
if (pumpIsOn && pumpCurrent > 6.0) {
    sendNotification('⚠️ AquaGuard Alert - Pump Overload', 
                    `Pump is overloaded! Current: ${pumpCurrent.toFixed(1)}A - Pump turned off for safety.`);
} else if (pumpIsOn && pumpCurrent < 1.5) {
    sendNotification('⚠️ AquaGuard Alert - Pump Dry Run', 
                    `Pump dry run detected! Current: ${pumpCurrent.toFixed(1)}A - Pump turned off for safety.`);
} else if (pumpIsOn && pumpCurrent > 5.0) {
    sendNotification('⚠️ AquaGuard Alert - High Current', 
                    `Pump current is high (${pumpCurrent.toFixed(1)}A). Monitor for potential issues.`);
}
```

#### Connection Monitoring
```javascript
// Connection Failure Detection
function startConnectionMonitoring() {
    connectionCheckInterval = setInterval(() => {
        if (lastMessageTime) {
            const timeSinceLastMessage = new Date() - lastMessageTime;
            const secondsSinceLastMessage = timeSinceLastMessage / 1000;
            
            if (secondsSinceLastMessage > 10 && !connectionFailureNotified) {
                connectionFailureNotified = true;
                sendNotification('🔌 AquaGuard Alert - Connection Lost', 
                                'Device or WebSocket connection lost for more than 10 seconds. Please check your connection.');
            }
        }
    }, 5000);
}
```

### Notification Delivery Methods

#### Browser Notifications
- **API**: Browser Notifications API
- **Permission Handling**: Automatic permission request
- **Auto-close**: 5-second timeout
- **Custom Icons**: System logo integration

#### Firebase Cloud Messaging (FCM)
- **Service Worker**: `firebase-messaging-sw.js`
- **Background Notifications**: Works when browser is closed
- **Mobile Support**: Native mobile app integration

---

## WebSocket Communication

### Connection Management
```javascript
// WebSocket Connection Setup
const deviceId = document.getElementById('device-id').getAttribute('content');
const socket = new WebSocket(`wss://${window.location.host}/ws/dashboard/${deviceId}/`);

socket.onopen = function(e) {
    console.log('WebSocket connection established');
    updateConnectionStatus('websocket', 'Connected', 'online');
};

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    window.lastData = data;
    lastMessageTime = new Date();
    connectionFailureNotified = false;
    
    // Process real-time data
    updateTankLevelsLive(data);
    updateStatusMessagesLive(data);
    updateLiveAnalytics(data);
};

socket.onclose = function(e) {
    console.log('WebSocket connection closed');
    updateConnectionStatus('websocket', 'Offline', 'offline');
};

socket.onerror = function(e) {
    console.error('WebSocket error:', e);
    updateConnectionStatus('websocket', 'Error', 'error');
};
```

### Data Flow
1. **Device → WebSocket**: IoT device sends sensor data
2. **WebSocket → Dashboard**: Real-time data updates dashboard
3. **Dashboard → Notifications**: Trigger alerts based on thresholds
4. **Dashboard → Device**: Send control commands (pump ON/OFF)

### Message Format
```json
{
    "tank_1_level": 75.5,
    "tank_2_level": 45.2,
    "pump_status": true,
    "pump_current": 3.2,
    "system_status": "normal",
    "mode": "auto",
    "timestamp": "2024-12-19T10:30:00Z"
}
```

---

## Database Schema

### Device Model
```python
class Device(models.Model):
    name = models.CharField(max_length=100)
    device_id = models.CharField(max_length=50, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # Tank Configuration
    tank_1_name = models.CharField(max_length=50, blank=True)
    tank_1_reading_id = models.CharField(max_length=50, blank=True)
    tank_1_capacity_liters = models.PositiveIntegerField(default=500)
    
    tank_2_name = models.CharField(max_length=50, blank=True)
    tank_2_reading_id = models.CharField(max_length=50, blank=True)
    tank_2_capacity_liters = models.PositiveIntegerField(default=500)
    
    tank_3_name = models.CharField(max_length=50, blank=True)
    tank_3_reading_id = models.CharField(max_length=50, blank=True)
    tank_3_capacity_liters = models.PositiveIntegerField(default=500)
    
    tank_4_name = models.CharField(max_length=50, blank=True)
    tank_4_reading_id = models.CharField(max_length=50, blank=True)
    tank_4_capacity_liters = models.PositiveIntegerField(default=500)
    
    # Solenoid Configuration
    solenoid_1_name = models.CharField(max_length=50, blank=True)
    solenoid_1_reading_id = models.CharField(max_length=50, blank=True)
    
    # Source Tank Configuration
    source_tank = models.PositiveIntegerField(choices=[(1, 'Tank 1'), (2, 'Tank 2'), (3, 'Tank 3'), (4, 'Tank 4')], default=1)
    
    def get_tank_config(self):
        """Return list of configured tanks"""
        tanks = []
        for i in range(1, 5):
            name = getattr(self, f"tank_{i}_name", None)
            reading_id = getattr(self, f"tank_{i}_reading_id", None)
            capacity = getattr(self, f"tank_{i}_capacity_liters", 500) or 500
            if name and reading_id:
                tanks.append({
                    "name": name,
                    "data_key": reading_id,
                    "capacity": capacity
                })
        return tanks
```

### Water Reading Model
```python
class WaterReading(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    reading_id = models.CharField(max_length=50)
    level = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
```

---

## API Endpoints

### WebSocket Endpoints
- **Dashboard WebSocket**: `/ws/dashboard/<device_id>/`
- **Consumer**: `DashboardConsumer`
- **Authentication**: Device-based authentication

### HTTP Endpoints
- **Dashboard**: `/dashboard/<device_id>/`
- **Device List**: `/devices/`
- **Login**: `/login/`
- **Logout**: `/logout/`
- **Password Change**: `/change-password/`
- **AI Chat**: `/api/ai_chat/`

### API Response Formats
```json
// Dashboard Data
{
    "device": {
        "name": "AquaGuard_Device_01",
        "tank_config": [
            {
                "name": "Overhead Tank",
                "data_key": "overhead_level",
                "capacity": 500
            }
        ]
    },
    "websocket_url": "wss://domain.com/ws/dashboard/AquaGuard_Device_01/"
}
```

---

## Configuration Management

### Django Settings
```python
# WebSocket Configuration
ASGI_APPLICATION = 'AquaGuard.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379')],
        },
    },
}

# Static Files Configuration
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'dashboard' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Notification Configuration
FCM_SERVER_KEY = os.environ.get('FCM_SERVER_KEY')
FCM_SENDER_ID = os.environ.get('FCM_SENDER_ID')
```

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

---

## Deployment Guide

### Railway Deployment
1. **Connect Repository**: Link GitHub repository to Railway
2. **Environment Variables**: Set required environment variables
3. **Database**: Configure PostgreSQL database
4. **Redis**: Set up Redis for WebSocket support
5. **Static Files**: Configure static file serving
6. **Domain**: Set up custom domain (optional)

### Local Development Setup
```bash
# Clone Repository
git clone <repository-url>
cd AquaGuard_Django

# Install Dependencies
pip install -r requirements.txt

# Database Migration
python manage.py migrate

# Create Superuser
python manage.py createsuperuser

# Run Development Server
python manage.py runserver

# Run Channels Server (for WebSocket)
python manage.py runserver 0.0.0.0:8000
```

### Production Checklist
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Static files collected
- [ ] WebSocket server running
- [ ] Redis server accessible
- [ ] SSL certificate configured
- [ ] Firebase Cloud Messaging configured
- [ ] Monitoring and logging set up

---

## Monitoring and Logging

### System Monitoring
```javascript
// Connection Status Monitoring
function updateConnectionStatus(type, status, className) {
    const statusElement = document.querySelector(`.${type}-status`);
    if (statusElement) {
        statusElement.textContent = status;
        statusElement.className = `${type}-status ${className}`;
    }
}

// Performance Monitoring
console.log('📊 Performance Metrics:', {
    tanksUpdated: tanksUpdated,
    tanksCreated: tanksCreated,
    connectionTime: connectionTime,
    dataProcessingTime: dataProcessingTime
});
```

### Error Logging
```javascript
// Error Handling
socket.onerror = function(e) {
    console.error('WebSocket error:', e);
    updateConnectionStatus('websocket', 'Error', 'error');
    
    // Log error for debugging
    if (window.showNotification) {
        window.showNotification(
            '⚠️ AquaGuard Alert - Connection Error',
            'WebSocket connection error detected. Please check your connection.',
            '/static/images/logo.png'
        );
    }
};
```

### Log Analysis
- **Browser Console**: JavaScript errors and warnings
- **Network Tab**: WebSocket connection status
- **Performance Tab**: Page load and rendering times
- **Application Tab**: Local storage and session data

---

## Security Considerations

### Authentication
- **User Authentication**: Django's built-in authentication system
- **Device Authentication**: Device ID-based WebSocket authentication
- **Session Management**: Secure session handling

### Data Protection
- **HTTPS**: SSL/TLS encryption for all communications
- **CSRF Protection**: Cross-site request forgery protection
- **XSS Prevention**: Input sanitization and output escaping
- **SQL Injection Prevention**: Django ORM protection

### Notification Security
- **Permission-based**: User consent for notifications
- **Secure Messaging**: Encrypted notification delivery
- **Rate Limiting**: Prevent notification spam

---

## Performance Optimization

### Frontend Optimization
- **Static File Compression**: Gzip compression for CSS/JS
- **Image Optimization**: Optimized images and icons
- **Caching**: Browser caching for static assets
- **Lazy Loading**: Deferred loading of non-critical resources

### Backend Optimization
- **Database Queries**: Optimized queries with select_related
- **WebSocket Efficiency**: Minimal data transfer
- **Caching**: Redis caching for frequently accessed data
- **Connection Pooling**: Efficient database connections

### Monitoring Performance
- **Page Load Times**: Monitor dashboard load performance
- **WebSocket Latency**: Track real-time data delivery
- **Memory Usage**: Monitor browser memory consumption
- **CPU Usage**: Track client-side processing load

---

## Version History

### v1.5 (Current)
- **Real-time tank monitoring**
- **Comprehensive notification system**
- **Pump control and safety monitoring**
- **Live analytics and reporting**
- **Connection monitoring and alerts**
- **Mobile-responsive interface**

### Previous Versions
- **v1.0**: Basic tank monitoring
- **v1.1**: WebSocket integration
- **v1.2**: Pump control system
- **v1.3**: Notification system
- **v1.4**: Live analytics

---

*This technical documentation provides comprehensive information for system administrators and developers working with the AquaGuard system. For additional technical support or development questions, please refer to the codebase or contact the development team.*
