# AquaSavvy Analytics Dashboard Documentation

## Overview

The AquaSavvy Analytics Dashboard is a comprehensive, real-time analytics system designed to provide detailed insights into water usage, power consumption, and pump runtime data. The dashboard features a modern dark theme interface with dynamic charts, real-time updates, and comprehensive data export capabilities.

## Table of Contents

1. [Features Overview](#features-overview)
2. [Visual Design & Aesthetic](#visual-design--aesthetic)
3. [Dashboard Layout](#dashboard-layout)
4. [Chart Types & Functionality](#chart-types--functionality)
5. [Data Processing & Updates](#data-processing--updates)
6. [CSV Export Functionality](#csv-export-functionality)
7. [Security Implementation](#security-implementation)
8. [Technical Architecture](#technical-architecture)
9. [API Endpoints](#api-endpoints)
10. [Configuration & Setup](#configuration--setup)
11. [Troubleshooting](#troubleshooting)

## Features Overview

### Core Features
- **Real-time Analytics**: Live data updates with dynamic chart positioning
- **12-Month Rolling Window**: Chronological data display with automatic updates
- **Dark Theme Interface**: Modern, professional aesthetic matching reference design
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Comprehensive Data Export**: Multiple CSV download options
- **Interactive Charts**: Hover effects, tooltips, and smooth animations

### Data Types Analyzed
- **Water Usage**: Daily, monthly, and yearly consumption patterns
- **Power Consumption**: Electrical usage tracking and optimization
- **Pump Runtime**: Operational efficiency and maintenance insights
- **Peak Usage Patterns**: Power company reporting and optimization

## Visual Design & Aesthetic

### Color Scheme
- **Primary Background**: `#212529` (Dark charcoal/navy)
- **Card Background**: `#2c3034` (Slightly lighter charcoal)
- **Accent Colors**: `#3a3f44` (Border and hover states)
- **Text Colors**: `#ffffff` (Primary), `#adb5bd` (Secondary)

### Design Elements
- **Rounded Corners**: 12px border radius for cards, 8px for buttons
- **Box Shadows**: `0 4px 6px rgba(0, 0, 0, 0.3)` for depth
- **Typography**: Clean, modern fonts with proper hierarchy
- **Spacing**: Consistent 20px margins and padding

### Responsive Breakpoints
- **Desktop**: Full two-column layout
- **Tablet**: Single column with adjusted spacing
- **Mobile**: Optimized single column with touch-friendly elements

## Dashboard Layout

### Header Section
```
┌─────────────────────────────────────────────────────────┐
│ Analytical Dashboard                            ☰       │
└─────────────────────────────────────────────────────────┘
```

### Two-Column Grid Layout
```
┌─────────────────────────┬─────────────────────────┐
│   Water Usage Analytics │  Power & Pump Analytics │
│                         │                         │
│   KPI Display           │   KPI Display           │
│   Monthly Bar Chart     │   Combined Chart        │
│   Daily Usage Table     │   Power Pie Chart       │
│                         │   Peak Usage Table      │
│                         │   Daily Power Table     │
└─────────────────────────┴─────────────────────────┘
```

### Download Section
```
┌─────────────────────────────────────────────────────────┐
│ 📥 Download Data Reports                                │
│                                                         │
│ 💧 Water Usage Data    ⚡ Power & Runtime    📊 Complete│
│ [Daily] [Monthly] [Year] [Daily] [Monthly] [Year] [All]│
└─────────────────────────────────────────────────────────┘
```

## Chart Types & Functionality

### 1. Water Usage Bar Chart
- **Type**: Vertical bar chart
- **Data**: 12-month rolling window
- **Colors**: 12 distinct vibrant colors
- **Features**:
  - Dynamic month labels with year (e.g., "Jan 24")
  - Thousands separators for large numbers
  - Hover tooltips with exact values
  - Responsive scaling

### 2. Power & Runtime Combined Chart
- **Type**: Dual-axis chart (bar + line)
- **Left Y-Axis**: Power usage (kWh) - Orange bars
- **Right Y-Axis**: Pump runtime (hours) - Green line
- **Features**:
  - Dual y-axis for different data scales
  - Smooth line interpolation
  - Enhanced tooltips with units
  - Legend with color coding

### 3. Power Usage Pie Chart
- **Type**: Full circle pie chart (360°)
- **Data**: 12-month power distribution
- **Features**:
  - Dynamic angles based on data values
  - Starts from top (-90° rotation)
  - Percentage tooltips
  - Smooth 2-second animations
  - 12 distinct colors for months

### Chart Color Palette
```css
#42A5F5  /* Blue */
#66BB6A  /* Green */
#FFA726  /* Orange */
#EF5350  /* Red */
#AB47BC  /* Purple */
#7E57C2  /* Deep Purple */
#26A69A  /* Teal */
#FFCA28  /* Yellow */
#FF7043  /* Deep Orange */
#8D6E63  /* Brown */
#78909C  /* Blue Grey */
#9575CD  /* Light Purple */
```

## Data Processing & Updates

### Rolling 12-Month Window
The dashboard uses a rolling 12-month window that automatically updates based on the current date:

```python
# Current month: Shows data up to today
month_start = current_date.replace(day=1)
month_end = current_date

# Previous months: Full month data
for i in range(1, 12):
    month_date = current_date.replace(day=1) - timedelta(days=1)
    # Calculate proper month boundaries
```

### Dynamic Month Labels
```javascript
function generateMonthLabels() {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const currentDate = new Date();
    const labels = [];
    
    for (let i = 11; i >= 0; i--) {
        const date = new Date(currentDate.getFullYear(), 
                            currentDate.getMonth() - i, 1);
        labels.push(months[date.getMonth()] + ' ' + 
                   date.getFullYear().toString().slice(-2));
    }
    return labels;
}
```

### Real-Time Update Function
```javascript
window.updateAnalyticsCharts = function(newWaterData, newPowerData, newRuntimeData) {
    // Update water usage chart
    waterUsageCtx.chart.data.datasets[0].data = padDataArray([...newWaterData]);
    waterUsageCtx.chart.update('active');
    
    // Update power/runtime chart
    powerRuntimeCtx.chart.data.datasets[0].data = padDataArray([...newPowerData]);
    powerRuntimeCtx.chart.data.datasets[1].data = padDataArray([...newRuntimeData]);
    powerRuntimeCtx.chart.update('active');
    
    // Update power pie chart
    powerPieCtx.chart.data.datasets[0].data = padDataArray([...newPowerData]);
    powerPieCtx.chart.update('active');
};
```

## CSV Export Functionality

### Available Export Types

#### 1. Water Usage Data
- **Daily (30 days)**: Recent daily water usage and storage
- **Monthly (1 year)**: 12-month aggregated water data
- **Yearly (3 years)**: Long-term water usage trends

#### 2. Power & Runtime Data
- **Daily (30 days)**: Recent power consumption and pump runtime
- **Monthly (1 year)**: 12-month power and runtime aggregation
- **Yearly (3 years)**: Long-term power and operational data

#### 3. Comprehensive Report
- **Complete Report (30 days)**: All data types combined
- **Includes**: Water usage, power consumption, pump runtime, device information

### CSV File Structure
```csv
Date,Device,Water Usage (L),Water Stored (L),Power (kWh),Runtime (h)
2024-01-15,Device_001,1250.5,850.0,45.2,12.5
2024-01-15,Device_002,980.3,720.0,38.7,10.2
```

### Download Endpoints
- `/AquaSavvy-Control/dashboard/device/analytics/download_csv/water_usage/`
- `/AquaSavvy-Control/dashboard/device/analytics/download_csv/power_runtime/`
- `/AquaSavvy-Control/dashboard/device/analytics/download_csv/`

## Security Implementation

### XSS Prevention
All template variables are properly escaped using Django's `|escapejs` filter:

```html
<script>
const waterUsageData = JSON.parse('{{ monthly_water_usage|escapejs }}');
const powerData = JSON.parse('{{ monthly_power_usage|escapejs }}');
</script>
```

### Authentication & Authorization
- **Login Required**: All analytics views require authentication
- **Device Ownership**: Users can only access their own device data
- **Admin Access**: Analytics dashboard accessible via custom admin URL

### Input Validation
- **JSON Parsing**: Safe JSON parsing with error handling
- **Data Sanitization**: All user inputs are sanitized
- **SQL Injection Prevention**: Django ORM with parameterized queries

### Security Headers
```python
# Enhanced security middleware
class EnhancedSecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        return response
```

## Technical Architecture

### Frontend Technologies
- **Chart.js 3.9.1**: Interactive chart library
- **HTML5/CSS3**: Modern web standards
- **JavaScript ES6+**: Modern JavaScript features
- **Responsive Grid**: CSS Grid and Flexbox

### Backend Technologies
- **Django 4.2+**: Web framework
- **PostgreSQL**: Database for data storage
- **Django ORM**: Database abstraction layer
- **JSON Serialization**: Data format for frontend

### Data Flow
```
Database → Django Views → JSON Serialization → Chart.js → Interactive Charts
    ↓
CSV Export ← Django Admin Views ← Data Aggregation ← Database Queries
```

### File Structure
```
dashboard/
├── templates/admin/
│   └── analytics.html          # Main dashboard template
├── admin.py                    # Admin views and CSV exports
├── models.py                   # Data models
├── views.py                    # Dashboard views
└── security_decorators.py      # Security middleware
```

## API Endpoints

### Analytics Dashboard
- **URL**: `/AquaSavvy-Control/dashboard/device/analytics/`
- **Method**: GET
- **Authentication**: Required
- **Response**: HTML dashboard with embedded JSON data

### CSV Downloads
- **Water Usage**: `/AquaSavvy-Control/dashboard/device/analytics/download_csv/water_usage/`
- **Power & Runtime**: `/AquaSavvy-Control/dashboard/device/analytics/download_csv/power_runtime/`
- **Comprehensive**: `/AquaSavvy-Control/dashboard/device/analytics/download_csv/`

### Query Parameters
- `period=daily`: Last 30 days
- `period=monthly`: Last 12 months
- `period=yearly`: Last 3 years

## Configuration & Setup

### Environment Variables
```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database
DB_PASSWORD=secure_password

# Django Configuration
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com

# Admin Configuration
ADMIN_URL=AquaSavvy-Control/
```

### Database Migration
```bash
# Create migration for new field
python manage.py makemigrations dashboard

# Apply migration
python manage.py migrate
```

### Static Files
```bash
# Collect static files
python manage.py collectstatic

# Serve static files in development
python manage.py runserver
```

## Troubleshooting

### Common Issues

#### 1. Charts Not Displaying
**Symptoms**: Blank chart areas
**Solutions**:
- Check browser console for JavaScript errors
- Verify Chart.js CDN is loading
- Ensure data arrays are not empty
- Check for JSON parsing errors

#### 2. Data Not Updating
**Symptoms**: Charts show old data
**Solutions**:
- Clear browser cache
- Check database for new records
- Verify date range calculations
- Restart Django server

#### 3. CSV Downloads Failing
**Symptoms**: Download links not working
**Solutions**:
- Check file permissions
- Verify URL patterns in admin.py
- Check for missing data
- Review server logs

#### 4. Performance Issues
**Symptoms**: Slow loading or freezing
**Solutions**:
- Limit data range for large datasets
- Add database indexes
- Implement data pagination
- Use database query optimization

### Debug Mode
Enable debug mode for development:
```python
# settings.py
DEBUG = True
```

### Logging Configuration
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'analytics.log',
        },
    },
    'loggers': {
        'dashboard': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

## Performance Optimization

### Database Optimization
- **Indexes**: Add indexes on date and device fields
- **Query Optimization**: Use select_related and prefetch_related
- **Connection Pooling**: Configure database connection pooling

### Frontend Optimization
- **Chart.js Optimization**: Use responsive and maintainAspectRatio options
- **Data Caching**: Implement client-side data caching
- **Lazy Loading**: Load charts only when visible

### Caching Strategy
```python
# Redis caching for analytics data
from django.core.cache import cache

def get_analytics_data():
    cache_key = 'analytics_data_30_days'
    data = cache.get(cache_key)
    if not data:
        data = calculate_analytics_data()
        cache.set(cache_key, data, 300)  # 5 minutes
    return data
```

## Future Enhancements

### Planned Features
1. **Real-time WebSocket Updates**: Live data streaming
2. **Advanced Filtering**: Date range picker and device filters
3. **Export Formats**: PDF and Excel export options
4. **Alert System**: Threshold-based notifications
5. **Mobile App**: Native mobile application
6. **API Integration**: REST API for third-party integrations

### Technical Roadmap
1. **Microservices Architecture**: Separate analytics service
2. **Data Warehouse**: Dedicated analytics database
3. **Machine Learning**: Predictive analytics and anomaly detection
4. **Cloud Integration**: AWS/Azure cloud deployment
5. **IoT Integration**: Direct sensor data integration

## Support & Maintenance

### Regular Maintenance Tasks
- **Database Cleanup**: Archive old data
- **Performance Monitoring**: Track response times
- **Security Updates**: Keep dependencies updated
- **Backup Verification**: Test data recovery procedures

### Monitoring & Alerts
- **Uptime Monitoring**: Track dashboard availability
- **Error Tracking**: Monitor JavaScript and server errors
- **Performance Metrics**: Track page load times
- **User Analytics**: Monitor usage patterns

### Contact Information
- **Technical Support**: contact@vision072025@gmail.com
- **WhatsApp**: +254 702 715070
- **Documentation**: This file and related technical docs

---

**Last Updated**: January 2025
**Version**: 2.0
**Compatibility**: Django 4.2+, Chart.js 3.9.1+, Modern Browsers

*This documentation is maintained as part of the AquaSavvy IoT Water Management System.*
