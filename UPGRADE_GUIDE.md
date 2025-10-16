# AquaSavvy Solution - Major Upgrade Guide

## Overview
This upgrade transforms your AquaGuard system into a dynamic, scalable IoT platform with:
- ✅ **Dynamic Tank Support** (1, 2, or unlimited tanks)
- ✅ **User-Defined Automation Rules** (time-based pump control)
- ✅ **Modern Icon-Based UI** (FontAwesome icons for navigation)
- ✅ **Real-Time Analytics Charts** (Pump Runtime & Power Usage)
- ✅ **Power Consumption Tracking** (kWh calculation & monitoring)
- ✅ **Draggable AI Chat Widget** (movable floating button)
- ✅ **Device Connectivity Indicators** (WiFi status icons)

---

## 🚀 Deployment Steps

### Step 1: Database Migrations
Run these commands in your Railway shell or local environment:

```bash
# Create new migrations
python manage.py makemigrations dashboard

# Apply migrations to database
python manage.py migrate

# Verify migrations applied successfully
python manage.py showmigrations dashboard
```

**Expected Changes:**
- New `AutomationRule` model
- `WaterReading.tank_data` JSONField added
- `WaterReading.pump_current_amps`, `pump_mode` added
- `DailyWaterUsage.total_power_kwh`, `pump_runtime_hours`, `total_stored_liters` added

### Step 2: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

###Step 3: Set Environment Variables
Ensure these are set in Railway:
- `GEMINI_API_KEY` - For AI chat assistant
- `SECRET_KEY` - Django secret key
- `DATABASE_URL` - PostgreSQL connection string (auto-configured by Railway)

### Step 4: Test the Deployment
1. Visit your Railway URL
2. Login to the admin panel
3. Check that you can see the new `AutomationRule` model
4. Open a device dashboard and verify dynamic tank rendering

---

## 📊 New Features Explanation

### 1. Dynamic Tank Architecture

**ESP32 Payload Format (NEW):**
```json
{
  "tank_data": [
    {"name": "Underground", "level": 45},
    {"name": "Overhead", "level": 82},
    {"name": "Storage", "level": 60}  // Optional 3rd tank
  ],
  "pump_status": true,
  "pump_current_amps": 3.5,
  "pump_mode": "AUTO",
  "system_status": "OK"
}
```

**Backward Compatibility:**
The system still accepts the old format:
```json
{
  "overhead_level": 82,
  "underground_level": 45,
  "pump_status": true,
  "pump_current": 3.5,
  "system_status": "OK"
}
```

The backend automatically converts old format to new format internally.

### 2. Automation Rules (User-Defined Timeslots)

Users can now create custom automation rules in the Django admin that override system behavior during specific times.

**Example Rule:**
- **Name:** "Night Time Pumping"
- **Active:** 22:00 - 06:00
- **Pump ON when:** Overhead tank ≤ 20%
- **Pump OFF when:** Overhead tank ≥ 90%
- **Destination Tank:** Overhead

**How It Works:**
1. User creates a rule in the admin panel
2. System checks if any enabled rule is currently active
3. If active, rule's min/max levels override default system logic
4. If no rule active, falls back to default auto-mode

**TO IMPLEMENT:** The actual pump control logic needs to be integrated into `consumers.py` or `notifications.py`. Currently, the model and UI are ready, but the automation logic execution is **not yet connected**.

### 3. Icon-Based Navigation

All navigation buttons now use FontAwesome icons:
- **←** Back to Devices
- **📖** Documentation
- **🚪** Logout
- **🔔** Enable Notifications
- **📶** Device WiFi Status (dynamic color)

### 4. Analytics Charts

Two new Chart.js visualizations on the dashboard:
- **Pump Runtime Chart (Pie):** Shows % time pump was ON vs OFF in last 24h
- **Power Usage Chart (Bar):** Displays average current draw for each hour

**NOTE:** These charts are initialized but currently show placeholder data. To populate with real data, you need to:
1. Query `WaterReading` data for the last 24 hours
2. Calculate hourly averages
3. Pass data to JavaScript via the Django template context
4. Update the chart data in `dashboard.js`

### 5. Power Consumption Tracking

The system now calculates and stores daily power consumption:

**Formula:**
```
kWh = (pump_runtime_hours × avg_current_amps × 240V) / 1000
```

**Stored in:** `DailyWaterUsage.total_power_kwh`

**Aggregation:** Runs daily via `python manage.py aggregate_usage`

**Retention:**
- Raw readings: 48 hours
- Daily summaries: 35 days
- For long-term (3+ years), create `MonthlyWaterUsage` model (see comments in `aggregate_usage.py`)

### 6. Draggable Chat Widget

The AI chat FAB (floating action button) can now be dragged vertically along the right side of the screen.

**User Experience:**
- **Drag:** Hold and drag the 💬 button up/down
- **Click:** Tap/click to open chat panel
- **Mobile-Friendly:** Supports touch gestures

---

## 🛠️ Files Modified

### Backend (Python)
1. **`dashboard/models.py`**
   - Added `AutomationRule` model
   - Added `tank_data` JSONField to `WaterReading`
   - Added power/runtime fields to `DailyWaterUsage`
   - Made legacy fields nullable for backward compat

2. **`dashboard/consumers.py`**
   - Updated to handle dynamic `tank_data` array
   - Converts old format to new format automatically
   - Sends both formats via WebSocket for compatibility

3. **`dashboard/admin.py`**
   - Registered `AutomationRule`, `Profile`
   - Added JSON display for `tank_data` in admin
   - Updated `DailyWaterUsage` admin to show power fields

4. **`dashboard/management/commands/aggregate_usage.py`**
   - Added power calculation logic
   - Added pump runtime estimation
   - Added comprehensive comments for long-term data strategy

### Frontend (HTML/CSS/JS)
5. **`dashboard/templates/dashboard.html`**
   - Dynamic tank rendering with `{% for tank in tank_data %}`
   - Added Automation Rules card with CRUD UI
   - Added Chart.js analytics cards
   - Replaced text nav with icon buttons
   - Added device WiFi status icon

6. **`dashboard/templates/device_list.html`**
   - Added WiFi status icon to each device card
   - Updated nav to use icon buttons

7. **`dashboard/static/dashboard.css`**
   - Added styles for icon buttons (circular, `.icon-btn`)
   - Added WiFi status color coding
   - Added automation rules card styles
   - Added chart card styles
   - Added draggable FAB styles

8. **`dashboard/static/dashboard.js`**
   - Updated `socket.onmessage` to handle dynamic tanks
   - Added WiFi icon update function
   - Added Chart.js initialization (Pie & Bar charts)

9. **`dashboard/static/chat.js`**
   - Added drag-and-drop functionality
   - Touch-friendly for mobile devices
   - Distinguishes between click and drag gestures

---

## ⚠️ Known Issues & TODOs

### Critical TODOs (User Action Required)

1. **Pump Control Logic NOT Implemented**
   - The `AutomationRule` model and UI exist
   - **BUT:** The actual logic to check and apply rules is not yet implemented
   - **Action Required:** Integrate rule checking into `consumers.py` before pump commands
   - **Reference:** See Phase 2 Task 2.4 in the original requirements

2. **Chart Data Not Populated**
   - Charts are displayed but show placeholder data
   - **Action Required:** Query last 24h of readings in `dashboard_view` and pass to template
   - **Suggested Approach:**
     ```python
     # In dashboard/views.py
     from django.db.models import Avg
     from datetime import timedelta

     # Get 24h pump runtime data
     hourly_data = WaterReading.objects.filter(
         device=device,
         timestamp__gte=timezone.now() - timedelta(hours=24)
     ).extra(select={'hour': 'EXTRACT(hour FROM timestamp)'}) \
      .values('hour') \
      .annotate(avg_current=Avg('pump_current_amps'))

     context['hourly_data'] = list(hourly_data)
     ```

3. **Admin Analytics Dashboard**
   - Old `AnalyticsAdminSite` was removed to avoid conflicts
   - **Action Required:** Re-implement custom admin view for data analytics
   - **Files to Create:**
     - `dashboard/templates/admin/analytics_dashboard.html`
     - Add custom view to `dashboard/admin.py`
     - Add URL pattern in `AquaGuard/urls.py`

### Non-Critical Enhancements

4. **CRUD Endpoints for Automation Rules**
   - The dashboard shows rules but Edit/Delete buttons don't work yet
   - **Action Required:** Create Django views/URLs for create/edit/delete operations
   - **Alternative:** Users can manage rules via Django admin for now

5. **Real-Time Rule Status Indicator**
   - Show which rule (if any) is currently active on the dashboard
   - **Suggested:** Add a badge to the Automation Rules card

---

## 🧪 Testing Checklist

After deployment, test these features:

- [ ] Device list shows WiFi status icons (initially offline)
- [ ] Dashboard displays dynamic tanks (should work with 1, 2, or 3+ tanks)
- [ ] Navigation uses icon buttons (back, docs, logout)
- [ ] AI chat FAB can be dragged vertically
- [ ] Pump status shows "True/False" correctly
- [ ] Pump mode displays "AUTO", "MANUAL", or "TIMESLOT"
- [ ] Charts render (even with placeholder data)
- [ ] Admin panel shows `AutomationRule` model
- [ ] Can create a new automation rule in admin
- [ ] `python manage.py aggregate_usage` runs without errors
- [ ] Old ESP32 payload format still works (backward compat)
- [ ] New ESP32 payload format displays correctly

---

## 📞 Support

For questions or issues:
- **Email:** contact:vision072025@gmail.com
- **WhatsApp:** +254 702 715070

**Next Steps:**
1. Run migrations on your deployment (Railway)
2. Test dynamic tank rendering with sample data
3. Implement automation rule logic (pump control)
4. Populate charts with real data
5. Add CRUD endpoints for automation rules (optional)
6. Re-implement admin analytics dashboard

---

## 📝 ESP32 Firmware Update Guide

To take advantage of dynamic tanks, update your ESP32 firmware to send:

```cpp
// NEW: Multi-tank JSON format
StaticJsonDocument<256> doc;
JsonArray tanks = doc.createNestedArray("tank_data");
JsonObject tank1 = tanks.createNestedObject();
tank1["name"] = "Underground";
tank1["level"] = underground_level;
JsonObject tank2 = tanks.createNestedObject();
tank2["name"] = "Overhead";
tank2["level"] = overhead_level;

doc["pump_status"] = pump_is_on;
doc["pump_current_amps"] = current_reading;
doc["pump_mode"] = "AUTO"; // or "MANUAL", "TIMESLOT"
doc["system_status"] = "OK";

char buffer[256];
serializeJson(doc, buffer);
client.publish(topic, buffer);
```

**Note:** Old firmware will still work! The backend handles both formats.

---

## 🎉 Congratulations!

Your AquaSavvy Solution is now:
- **Scalable** (supports any number of tanks)
- **Customizable** (user-defined automation rules)
- **Data-Driven** (power analytics & consumption tracking)
- **Professional** (modern icon-based UI)
- **User-Friendly** (draggable chat, responsive design)

**Good luck with your deployment!** 🚀💧

