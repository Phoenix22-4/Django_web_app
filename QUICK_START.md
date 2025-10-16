# 🚀 AquaSavvy Solution - Quick Start Guide

## Immediate Actions Required

### 1. Run Migrations (CRITICAL)
```bash
python manage.py makemigrations dashboard
python manage.py migrate
```

### 2. Verify Installation
```bash
python manage.py check
python manage.py showmigrations dashboard
```

### 3. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 4. Restart Your Server
On Railway: Redeploy the application

---

## Access Points

| Feature | URL | Who Can Access |
|---------|-----|----------------|
| Public Home | `/home/` | Everyone |
| Login | `/login/` | All users |
| Device List | `/devices/` | Logged-in users |
| Dashboard | `/dashboard/{device_id}/` | Device owners |
| Admin Panel | `/admin/` | Staff only |
| **Analytics** | `/admin/analytics/` | Staff only |
| AI Chat | Floating button (all pages) | All users |

---

## New Models Added

1. **AutomationRule** - User-defined time-based pump control rules
2. **Profile** - Extended user model (phone number for notifications)

## Updated Models

1. **WaterReading**
   - Added: `tank_data` (JSONField)
   - Added: `pump_current_amps`, `pump_mode`
   - Made nullable: `overhead_level`, `underground_level`

2. **DailyWaterUsage**
   - Added: `total_power_kwh`, `pump_runtime_hours`, `total_stored_liters`

---

## ESP32 Payload Formats

### NEW FORMAT (Recommended)
```json
{
  "tank_data": [
    {"name": "Underground", "level": 45},
    {"name": "Overhead", "level": 82}
  ],
  "pump_status": true,
  "pump_current_amps": 3.5,
  "pump_mode": "AUTO",
  "system_status": "OK"
}
```

### OLD FORMAT (Still Works)
```json
{
  "overhead_level": 82,
  "underground_level": 45,
  "pump_status": true,
  "pump_current": 3.5,
  "system_status": "OK"
}
```

---

## Management Commands

### Daily Aggregation
```bash
python manage.py aggregate_usage
```
**Schedule:** Run this daily via cron job
**Purpose:** Calculate power consumption and clean old data

### Check Connectivity
```bash
python manage.py check_connectivity
```
**Schedule:** Run every 30 minutes
**Purpose:** Send offline alerts for devices

---

## Testing Checklist

```bash
# 1. Check migrations applied
python manage.py showmigrations dashboard

# 2. Create a superuser (if needed)
python manage.py createsuperuser

# 3. Run development server
python manage.py runserver

# 4. Visit these URLs:
# - http://localhost:8000/home/
# - http://localhost:8000/admin/
# - http://localhost:8000/admin/analytics/
# - http://localhost:8000/devices/
```

---

## Common Issues & Fixes

### "column dashboard_device.last_alert_type does not exist"
**Fix:** Run migrations
```bash
python manage.py migrate
```

### "Static files not loading"
**Fix:** Collect static files
```bash
python manage.py collectstatic --noinput
```

### "GEMINI_API_KEY not set"
**Fix:** Add environment variable in Railway
```
GEMINI_API_KEY=your_key_here
```

### "Charts not showing data"
**Expected:** Charts show placeholder data until you populate them with real readings

---

## Quick Wins

✅ **Automation Rules:** Create one via Admin → Automation Rules → Add  
✅ **Analytics:** Visit `/admin/analytics/` to see power usage graphs  
✅ **Chat Widget:** Drag the 💬 button up or down  
✅ **WiFi Icons:** Check device list for green/red connection status  
✅ **Icon Navigation:** Hover over circular buttons for tooltips  

---

## What Changed?

### User-Facing
- Dynamic tank support (1-3+ tanks)
- Automation rules for custom schedules
- Icon-based navigation
- Draggable AI chat
- WiFi status indicators

### Admin-Facing
- Analytics dashboard with charts
- CSV export
- Power consumption tracking
- Automation rule management

### Backend
- Improved data efficiency
- Power calculation logic
- Automation engine
- Backward compatibility

---

## Need Help?

📧 **Email:** contact:vision072025@gmail.com  
📱 **WhatsApp:** +254 702 715070  
📖 **Full Docs:** See `UPGRADE_GUIDE.md` and `IMPLEMENTATION_SUMMARY.md`

---

**Remember:** All old ESP32 firmware still works! You don't need to update devices immediately.

🎉 **You're ready to go!**

