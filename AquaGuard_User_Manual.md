# AquaGuard Dashboard - User Manual

## Table of Contents
1. [Overview](#overview)
2. [Dashboard Features](#dashboard-features)
3. [Notification System](#notification-system)
4. [Tank Management](#tank-management)
5. [Pump Control](#pump-control)
6. [System Monitoring](#system-monitoring)
7. [Troubleshooting](#troubleshooting)
8. [Safety Features](#safety-features)

---

## Overview

AquaGuard is an intelligent water management system that provides real-time monitoring, automated controls, and comprehensive notifications for your water tank system. The dashboard offers live analytics, pump control, and safety monitoring to ensure optimal water management.

### Key Features
- **Real-time tank level monitoring**
- **Automated pump control**
- **Live analytics and reporting**
- **Comprehensive notification system**
- **Safety monitoring and alerts**
- **Mobile-responsive interface**

---

## Dashboard Features

### Main Dashboard Layout

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

### System Status Panel
- **Connection Status**: WebSocket and device connectivity
- **Mode Status**: Current operation mode (Auto/Timeslot)
- **Pump Status**: Real-time pump state and current readings
- **Safety Status**: Critical alerts and warnings

---

## Notification System

AquaGuard provides comprehensive notifications for all critical system events. Notifications are sent to your browser and mobile device.

### Tank Level Notifications

#### Source Tank Alerts
- **🚨 Critical Level** (< 10%): 
  - *"TankName is critically low at X%! Please refill immediately."*
  - Triggers automatic pump shutdown for safety

- **⚠️ Low Level** (< 25%): 
  - *"TankName is running low at X%. Use water sparingly."*
  - Recommends water conservation

- **✅ Full Level** (≥ 95%): 
  - *"TankName is full at X%. Water level is optimal."*
  - Confirms optimal water storage

#### Secondary Tank Alerts
- **🚨 Minimum Level** (< 15%): 
  - *"TankName is at minimum level (X%). Please refill soon."*
  - Indicates need for water supply

- **✅ Full Level** (≥ 95%): 
  - *"TankName is full at X%. Water level is optimal."*
  - Confirms tank capacity reached

### Pump Safety Notifications

#### Current Sensor Monitoring
- **⚠️ Pump Overload** (Current > 6A): 
  - *"Pump is overloaded! Current: X.XA - Pump turned off for safety."*
  - Automatic safety shutdown

- **⚠️ Dry Run Detection** (Current < 1.5A when pump ON): 
  - *"Pump dry run detected! Current: X.XA - Pump turned off for safety."*
  - Prevents pump damage from running dry

- **⚠️ High Current Warning** (Current > 5A): 
  - *"Pump current is high (X.XA). Monitor for potential issues."*
  - Early warning for potential problems

#### Pump Status Changes
- **🟢 Pump Started**: 
  - *"Pump is ON. Current: X.XA"*
  - Confirms pump activation

- **🔴 Pump Stopped**: 
  - *"Pump is OFF"*
  - Confirms pump deactivation

### Connection Monitoring

#### Device/WebSocket Alerts
- **🔌 Connection Lost** (> 10 seconds): 
  - *"Device or WebSocket connection lost for more than 10 seconds. Please check your connection."*
  - Indicates communication failure with your device

### System Security Notifications

#### Password Change Alerts
- **🔐 Password Changed**: 
  - *"Your system password was changed by [username] at [date/time]."*
  - Security notification with timestamp and user information

---

## Tank Management

### Tank Configuration
1. **Access Django Admin**: Navigate to admin panel
2. **Select Device**: Choose your AquaGuard device
3. **Configure Tanks**:
   - **Tank Name**: Enter descriptive name (e.g., "Overhead Tank", "Underground Tank")
   - **Reading ID**: Set unique identifier for sensor data
   - **Capacity**: Enter tank capacity in liters
   - **Is Source**: Check box for source tanks (underground, well, etc.)

### Tank Display Features
- **Real-time Levels**: Live percentage and volume display
- **Capacity Information**: Shows current volume vs. total capacity
- **Visual Indicators**: Color-coded status (red=critical, orange=low, blue=full)
- **Source Tank Marking**: Special "(Source)" indicator for supply tanks

### Tank Status Messages
- **Critical**: Tank level below safe threshold
- **Low**: Tank approaching minimum level
- **Normal**: Tank operating within safe range
- **Full**: Tank at maximum capacity

---

## Pump Control

### Manual Pump Control
1. **Pump ON Button**: Manually start pump operation
2. **Pump OFF Button**: Manually stop pump operation
3. **Safety Checks**: System verifies source tank levels before activation

### Automated Pump Control
- **Auto Mode**: Pump operates based on tank levels and system logic
- **Timeslot Mode**: Pump operates according to scheduled times
- **Safety Override**: Automatic shutdown for critical conditions

### Pump Monitoring
- **Current Sensor**: Real-time current monitoring for safety
- **Animation**: Visual pump status with rotation indicator
- **Status Display**: ON/OFF state with current readings

---

## System Monitoring

### Live Analytics
- **24-Hour Water Usage**: Daily water consumption tracking
- **24-Hour Pump Usage**: Daily pump operation hours
- **Real-time Updates**: Live data refresh every minute
- **Daily Reset**: Analytics reset at midnight

### Connection Status
- **WebSocket Status**: Real-time communication status
- **Device Status**: Hardware connectivity indicator
- **Connection Monitoring**: Automatic failure detection after 10 seconds

### System Status Messages
- **Mode Status**: Current operation mode display
- **Pump Status**: Real-time pump state
- **Safety Status**: Critical condition alerts
- **Tank Status**: Individual tank level summaries

---

## Troubleshooting

### Common Issues

#### Tanks Not Displaying
- **Check Configuration**: Ensure tanks are configured in Django admin
- **Verify Reading IDs**: Confirm sensor data keys match configuration
- **Refresh Dashboard**: Reload page to initialize tank displays

#### Pump Not Responding
- **Check Connection**: Verify WebSocket connection is active
- **Safety Status**: Check for safety shutdown conditions
- **Manual Override**: Use manual controls if automatic system fails

#### Notifications Not Working
- **Browser Permissions**: Allow notifications in browser settings
- **Check Console**: Look for JavaScript errors in browser console
- **Network Connection**: Ensure stable internet connection

#### Connection Issues
- **Device Status**: Check hardware connectivity
- **WebSocket Status**: Verify real-time communication
- **Network Issues**: Check internet connection and firewall settings

### Error Messages

#### "Tank not configured in admin"
- **Solution**: Configure tank in Django admin with name and reading ID
- **Action**: Add tank configuration and refresh dashboard

#### "WebSocket not connected"
- **Solution**: Check network connection and device status
- **Action**: Refresh page or restart device if necessary

#### "Source tank level too low"
- **Solution**: Refill source tank before operating pump
- **Action**: Wait for tank to reach safe level or refill manually

---

## Safety Features

### Automatic Safety Shutdowns
- **Source Tank Critical**: Pump stops when source tank < 10%
- **Pump Overload**: Pump stops when current > 6A
- **Dry Run Protection**: Pump stops when current < 1.5A
- **Connection Loss**: System alerts when device communication fails

### Safety Monitoring
- **Real-time Current Monitoring**: Continuous pump current tracking
- **Tank Level Monitoring**: Continuous water level tracking
- **Connection Monitoring**: Automatic communication failure detection
- **System Status Monitoring**: Real-time system health checks

### Emergency Procedures
1. **Manual Pump Shutdown**: Use OFF button for immediate stop
2. **System Reset**: Refresh dashboard page if issues persist
3. **Contact Support**: Use system logs for technical support
4. **Safety First**: Always prioritize water safety over convenience

---

## System Requirements

### Browser Compatibility
- **Chrome**: Version 80 or higher
- **Firefox**: Version 75 or higher
- **Safari**: Version 13 or higher
- **Edge**: Version 80 or higher

### Mobile Support
- **Responsive Design**: Optimized for mobile devices
- **Touch Controls**: Touch-friendly interface
- **Mobile Notifications**: Native notification support

### Network Requirements
- **Internet Connection**: Stable internet for WebSocket communication
- **Firewall Settings**: Allow WebSocket connections
- **Device Connectivity**: Ensure hardware device is online

---

## Support and Maintenance

### Regular Maintenance
- **Monitor Tank Levels**: Check levels regularly
- **Clean Sensors**: Maintain sensor cleanliness
- **Update System**: Keep software updated
- **Backup Configuration**: Save tank and system settings

### System Logs
- **Browser Console**: Check for JavaScript errors
- **Network Tab**: Monitor WebSocket connections
- **System Status**: Review connection and device status

### Getting Help
- **Check Documentation**: Refer to this manual first
- **System Status**: Review dashboard status indicators
- **Error Messages**: Note specific error messages
- **Contact Support**: Provide system logs and error details

---

## Version Information

**AquaGuard Dashboard v1.5**
- **Last Updated**: December 2024
- **Features**: Real-time monitoring, comprehensive notifications, safety systems
- **Compatibility**: Modern browsers, mobile devices, WebSocket communication

---

*This manual covers all current features of the AquaGuard dashboard. For additional support or feature requests, please contact your system administrator.*
