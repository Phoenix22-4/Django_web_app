# AquaGuard Dashboard - Quick Reference Guide

## 🚀 Quick Start

### Accessing the Dashboard
1. **Login**: Navigate to your AquaGuard dashboard URL
2. **Select Device**: Choose your device from the device list
3. **Monitor**: View real-time tank levels and pump status

### First-Time Setup
1. **Configure Tanks**: Go to Django admin → Devices → Select your device
2. **Set Tank Names**: Enter descriptive names (e.g., "Overhead Tank", "Underground Tank")
3. **Set Reading IDs**: Enter sensor data keys (e.g., "overhead_level", "underground_level")
4. **Set Capacities**: Enter tank capacities in liters
5. **Mark Source Tank**: Check "Is Source" for your main water supply tank

---

## 📱 Notification Quick Reference

### Tank Level Alerts
| Level | Source Tank | Secondary Tank | Action Required |
|-------|-------------|----------------|-----------------|
| < 10% | 🚨 Critical | 🚨 Minimum | **Refill immediately** |
| < 25% | ⚠️ Low (Use sparingly) | Normal | Monitor closely |
| 15-95% | Normal | Normal | Normal operation |
| ≥ 95% | ✅ Full | ✅ Full | Optimal level |

### Pump Safety Alerts
| Condition | Current Reading | Alert | Action |
|-----------|----------------|-------|---------|
| Normal | 2-5A | ✅ Pump ON/OFF | Normal operation |
| High Current | > 5A | ⚠️ High Current | Monitor for issues |
| Overload | > 6A | 🚨 Overload | **Pump auto-stopped** |
| Dry Run | < 1.5A (when ON) | 🚨 Dry Run | **Pump auto-stopped** |

### Connection Alerts
| Status | Duration | Alert | Action |
|--------|----------|-------|---------|
| Connected | - | ✅ Online | Normal operation |
| Disconnected | > 10 seconds | 🔌 Connection Lost | **Check device/network** |

---

## 🎛️ Dashboard Controls

### Pump Control
- **Pump ON**: Green button - Manually start pump
- **Pump OFF**: Red button - Manually stop pump
- **Safety Check**: System verifies source tank level before starting

### Mode Selection
- **Auto Mode**: Pump operates automatically based on tank levels
- **Timeslot Mode**: Pump operates on scheduled times

### Tank Information
- **Tank Name**: Configured in Django admin
- **Level Percentage**: Real-time percentage display
- **Liters Remaining**: Current volume in tank
- **Capacity**: Total tank capacity in liters

---

## 🔧 Common Tasks

### Adding a New Tank
1. **Django Admin** → Devices → Select your device
2. **Find empty tank slot** (Tank 1-4)
3. **Enter tank name** (e.g., "Garden Tank")
4. **Enter reading ID** (e.g., "garden_level")
5. **Set capacity** (e.g., 300 liters)
6. **Save changes**
7. **Refresh dashboard** - Tank will appear automatically

### Changing Tank Configuration
1. **Django Admin** → Devices → Select your device
2. **Edit tank settings** (name, reading ID, capacity)
3. **Save changes**
4. **Refresh dashboard** - Changes will be reflected

### Setting Source Tank
1. **Django Admin** → Devices → Select your device
2. **Source Tank field** → Select tank number (1-4)
3. **Save changes**
4. **Refresh dashboard** - Source tank will be marked with "(Source)"

### Manual Pump Control
1. **Check source tank level** (must be > 10%)
2. **Click Pump ON button** (green)
3. **Monitor pump current** (should be 2-5A)
4. **Click Pump OFF button** (red) when done

---

## 🚨 Emergency Procedures

### Pump Won't Start
1. **Check source tank level** - Must be > 10%
2. **Check WebSocket connection** - Must be "Connected"
3. **Check safety status** - No critical alerts
4. **Try manual override** - Use Pump ON button

### Tank Not Showing
1. **Check Django admin configuration** - Tank must have name and reading ID
2. **Refresh dashboard page** - Tanks are created on page load
3. **Check browser console** - Look for JavaScript errors
4. **Verify reading ID** - Must match sensor data key

### Notifications Not Working
1. **Check browser permissions** - Allow notifications
2. **Check browser console** - Look for JavaScript errors
3. **Test notification** - Try changing tank levels
4. **Check network connection** - Ensure stable internet

### Connection Issues
1. **Check device status** - Ensure hardware is online
2. **Check WebSocket status** - Should show "Connected"
3. **Refresh page** - Reconnect WebSocket
4. **Check network** - Ensure stable internet connection

---

## 📊 Understanding the Dashboard

### Left Column - Live Analytics
- **Water Usage Chart**: 24-hour water consumption
- **Pump Usage Chart**: 24-hour pump operation hours
- **Mode Controls**: Auto/Timeslot selection
- **Timeslot Settings**: Scheduled operation controls

### Center Column - Live Tank Status
- **Tank Displays**: Real-time tank levels
- **Visual Indicators**: Color-coded status
- **Capacity Information**: Current vs. total capacity
- **Source Indicators**: Special marking for source tanks

### Right Column - Pump Control
- **Pump Animation**: Visual pump status
- **Control Buttons**: ON/OFF controls
- **Current Display**: Real-time current readings
- **Status Information**: Pump state and safety info

### Bottom - System Status
- **Connection Status**: WebSocket and device status
- **Mode Status**: Current operation mode
- **Pump Status**: Real-time pump state
- **Safety Status**: Critical alerts and warnings

---

## 🔍 Troubleshooting Quick Fixes

### Problem: Tanks not updating
**Solution**: Refresh dashboard page

### Problem: Pump button not working
**Solution**: Check WebSocket connection status

### Problem: Notifications not appearing
**Solution**: Check browser notification permissions

### Problem: Dashboard not loading
**Solution**: Check internet connection and refresh page

### Problem: Tank levels showing 0%
**Solution**: Check tank configuration in Django admin

### Problem: Pump animation not working
**Solution**: Check pump status and current readings

---

## 📞 Support Information

### Before Contacting Support
1. **Check this guide** for common solutions
2. **Check browser console** for error messages
3. **Note system status** indicators
4. **Document error messages** exactly

### Information to Provide
- **Device ID**: Your AquaGuard device identifier
- **Browser**: Browser type and version
- **Error Messages**: Exact error text from console
- **System Status**: Connection and device status
- **Steps to Reproduce**: What you were doing when the issue occurred

### System Requirements
- **Browser**: Chrome 80+, Firefox 75+, Safari 13+, Edge 80+
- **Internet**: Stable internet connection
- **Device**: AquaGuard hardware device online
- **Permissions**: Browser notification permissions enabled

---

## 🎯 Best Practices

### Regular Maintenance
- **Monitor tank levels** daily
- **Check system status** regularly
- **Clean sensors** monthly
- **Update system** when available

### Safety First
- **Never ignore critical alerts**
- **Check source tank levels** before pump operation
- **Monitor pump current** for safety
- **Respond to connection alerts** immediately

### Optimal Operation
- **Keep source tank** above 25%
- **Monitor pump current** (2-5A normal)
- **Use auto mode** for automatic operation
- **Set appropriate tank capacities** in admin

---

*This quick reference guide provides essential information for daily AquaGuard operation. For detailed information, refer to the complete User Manual.*
