# 📥 CSV Download Features - AquaSavvy Analytics

## 📋 Overview

The AquaSavvy system provides comprehensive CSV download functionality for analytics data through the Django admin interface. Users can download data in different formats and time periods for analysis and reporting.

## 🎯 Available Download Options

### 1. **Water Usage Data** 💧
**Separate CSV files for water-related metrics**

#### Download Options:
- **Daily (30 days)**: `aquasavvy_water_usage_daily.csv`
- **Monthly (1 year)**: `aquasavvy_water_usage_monthly.csv`
- **Yearly (3 years)**: `aquasavvy_water_usage_yearly.csv`

#### CSV Columns:
- `Device ID`: Unique device identifier
- `Date`: Date of the data entry
- `Water Usage (L)`: Total water consumed by users
- `Water Stored (L)`: Total water stored in tanks

### 2. **Power & Runtime Data** ⚡
**Separate CSV files for power and pump runtime metrics**

#### Download Options:
- **Daily (30 days)**: `aquasavvy_power_runtime_daily.csv`
- **Monthly (1 year)**: `aquasavvy_power_runtime_monthly.csv`
- **Yearly (3 years)**: `aquasavvy_power_runtime_yearly.csv`

#### CSV Columns:
- `Device ID`: Unique device identifier
- `Date`: Date of the data entry
- `Power (kWh)`: Total power consumed
- `Pump Runtime (h)`: Total pump operating hours

### 3. **Comprehensive Report** 📊
**Complete data report with all metrics combined**

#### Download Option:
- **Complete Report (30 days)**: `aquasavvy_30_day_comprehensive_report.csv`

#### CSV Columns:
- `Device ID`: Unique device identifier
- `Date`: Date of the data entry
- `Water Usage (L)`: Total water consumed by users
- `Water Stored (L)`: Total water stored in tanks
- `Power (kWh)`: Total power consumed
- `Pump Runtime (h)`: Total pump operating hours

## 🔧 Technical Implementation

### URL Endpoints

```python
# Water Usage Downloads
/admin/analytics/download_csv/water_usage/?period=daily
/admin/analytics/download_csv/water_usage/?period=monthly
/admin/analytics/download_csv/water_usage/?period=yearly

# Power & Runtime Downloads
/admin/analytics/download_csv/power_runtime/?period=daily
/admin/analytics/download_csv/power_runtime/?period=monthly
/admin/analytics/download_csv/power_runtime/?period=yearly

# Comprehensive Report
/admin/analytics/download_csv/
```

### Django Admin Views

```python
class DeviceAdmin(admin.ModelAdmin):
    def download_csv_water_usage(self, request):
        """Download water usage data only"""
        period = request.GET.get('period', 'daily')
        # Returns CSV with water usage and storage data
        
    def download_csv_power_runtime(self, request):
        """Download power and pump runtime data"""
        period = request.GET.get('period', 'daily')
        # Returns CSV with power and runtime data
        
    def download_csv(self, request):
        """Download comprehensive 30-day report"""
        # Returns CSV with all data types combined
```

## 📊 Data Time Periods

| Period | Days Covered | Use Case |
|--------|-------------|----------|
| **Daily** | 30 days | Short-term analysis, daily monitoring |
| **Monthly** | 365 days (1 year) | Medium-term trends, monthly reports |
| **Yearly** | 1095 days (3 years) | Long-term analysis, annual reports |

## 🎨 User Interface

### Analytics Dashboard Layout

```
┌─────────────────────────────────────────────────────────┐
│ Water Usage Analytics (Last 30 Days)    [All Data (30 Days)] │
├─────────────────────────────────────────────────────────┤
│ 📊 Statistics Cards (Usage, Power, Runtime, Devices)    │
├─────────────────────────────────────────────────────────┤
│ 📈 Charts (Pie Charts + Line Chart)                    │
├─────────────────────────────────────────────────────────┤
│ 📋 Daily Summary Table                                 │
├─────────────────────────────────────────────────────────┤
│ 📥 Download Data Reports                               │
│                                                         │
│ 💧 Water Usage Data        ⚡ Power & Runtime Data     │
│ [Daily] [Monthly] [Yearly] [Daily] [Monthly] [Yearly]  │
│                                                         │
│ 📊 Comprehensive Report                                 │
│ [Download Complete Report (30 Days)]                   │
└─────────────────────────────────────────────────────────┘
```

## 🔒 Security Features

### Access Control
- **Authentication Required**: All download endpoints require admin authentication
- **Admin View Protection**: Uses `self.admin_site.admin_view()` decorator
- **CSRF Protection**: All requests protected against CSRF attacks

### Data Privacy
- **Device ID Anonymization**: Device IDs are included but can be anonymized
- **Date Range Limiting**: Maximum 3 years of historical data
- **No Sensitive Data**: Only usage metrics, no personal information

## 📈 Use Cases

### 1. **Water Management Analysis**
- Download water usage data to analyze consumption patterns
- Identify peak usage periods and seasonal trends
- Monitor water storage efficiency

### 2. **Power Consumption Monitoring**
- Track power usage for cost analysis
- Monitor pump runtime for maintenance scheduling
- Identify energy efficiency opportunities

### 3. **System Performance Reports**
- Generate comprehensive reports for stakeholders
- Export data for external analysis tools
- Create monthly/quarterly business reports

### 4. **Maintenance Planning**
- Use pump runtime data for maintenance scheduling
- Monitor power consumption for equipment health
- Track usage patterns for capacity planning

## 🚀 Getting Started

### Accessing Downloads

1. **Login to Django Admin**
   - Navigate to `/AquaSavvy-Control/`
   - Login with admin credentials

2. **Access Analytics Dashboard**
   - Click on "Usage" in the admin dashboard
   - View the analytics dashboard with charts and tables

3. **Download Data**
   - Scroll to the "Download Data Reports" section
   - Choose the appropriate download option:
     - Water Usage Data (separate CSV)
     - Power & Runtime Data (separate CSV)
     - Comprehensive Report (all data)

### File Naming Convention

```
aquasavvy_[data_type]_[period].csv

Examples:
- aquasavvy_water_usage_daily.csv
- aquasavvy_power_runtime_monthly.csv
- aquasavvy_30_day_comprehensive_report.csv
```

## 🔧 Customization

### Adding New Data Types

To add new CSV download types:

1. **Add new view method** in `DeviceAdmin` class
2. **Add URL pattern** in `get_urls()` method
3. **Update template** with new download buttons
4. **Test functionality** with different time periods

### Modifying Time Periods

To change time period ranges:

```python
# In download methods, modify days_ago values
if period == 'daily':
    days_ago = 30  # Change this value
elif period == 'monthly':
    days_ago = 365  # Change this value
else:  # yearly
    days_ago = 1095  # Change this value
```

## 📞 Support

For technical support or questions about CSV downloads:
- **Email**: contact@vision072025@gmail.com
- **WhatsApp**: +254 702 715070

---

**Last Updated**: January 2025  
**Version**: 1.0.0  
**Status**: Production Ready ✅
