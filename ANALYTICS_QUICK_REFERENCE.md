# 📊 AquaSavvy Analytics Dashboard - Quick Reference

## 🚀 Quick Start

### Accessing the Dashboard
1. Navigate to: `/AquaSavvy-Control/dashboard/device/analytics/`
2. Login with admin credentials
3. View real-time analytics data

### Key Features at a Glance
- **Dark Theme Interface**: Professional, modern design
- **12-Month Rolling Data**: Always current, automatically updating
- **Interactive Charts**: Hover for details, smooth animations
- **CSV Exports**: Download data in multiple formats
- **Real-time Updates**: Charts refresh automatically

## 📈 Chart Types

### 1. Water Usage Bar Chart
- **Location**: Left column, top
- **Data**: 12 months of water consumption
- **Colors**: 12 distinct colors (one per month)
- **Features**: Thousands separators, hover tooltips

### 2. Power & Runtime Combined Chart
- **Location**: Right column, top
- **Data**: Power (bars) + Runtime (line)
- **Y-Axes**: Left (kWh), Right (hours)
- **Features**: Dual-axis comparison, enhanced tooltips

### 3. Power Usage Pie Chart
- **Location**: Right column, middle
- **Data**: 12-month power distribution
- **Features**: Dynamic angles, percentage tooltips
- **Animation**: 2-second smooth transitions

## 📊 Data Tables

### Daily Water Usage Table
- **Columns**: Date, Device, Usage (L), Stored (L)
- **Scope**: Current month data
- **Purpose**: Granular daily analysis

### Peak Usage Times Table
- **Columns**: Time, Device, Power (kWh), Runtime (h)
- **Scope**: Current month peak periods
- **Purpose**: Power company reporting

### Daily Power Usage Table
- **Columns**: Date, Device, Power (kWh), Runtime (h)
- **Scope**: Current month data
- **Purpose**: Daily power consumption tracking

## 📥 CSV Downloads

### Water Usage Data
- **Daily**: Last 30 days
- **Monthly**: Last 12 months
- **Yearly**: Last 3 years

### Power & Runtime Data
- **Daily**: Last 30 days
- **Monthly**: Last 12 months
- **Yearly**: Last 3 years

### Comprehensive Report
- **Complete**: All data types combined (30 days)
- **Includes**: Water, power, runtime, device info

## 🎨 Visual Elements

### Color Palette
```
Water Usage: #42A5F5 (Blue)
Power Usage: #FFA726 (Orange)
Runtime:     #4CAF50 (Green)
Background:  #212529 (Dark)
Cards:       #2c3034 (Charcoal)
```

### Chart Colors (12 Months)
```
Jan: #42A5F5  Jul: #26A69A
Feb: #66BB6A  Aug: #FFCA28
Mar: #FFA726  Sep: #FF7043
Apr: #EF5350  Oct: #8D6E63
May: #AB47BC  Nov: #78909C
Jun: #7E57C2  Dec: #9575CD
```

## 🔧 Technical Details

### Data Updates
- **Automatic**: Charts update when new data arrives
- **Manual**: Refresh page for latest data
- **Real-time**: Use `updateAnalyticsCharts()` function

### Browser Compatibility
- **Chrome**: ✅ Full support
- **Firefox**: ✅ Full support
- **Safari**: ✅ Full support
- **Edge**: ✅ Full support
- **Mobile**: ✅ Responsive design

### Performance
- **Load Time**: < 3 seconds
- **Chart Rendering**: < 1 second
- **Data Processing**: Real-time
- **Memory Usage**: Optimized for large datasets

## 🛠️ Troubleshooting

### Charts Not Loading
1. Check browser console for errors
2. Verify internet connection (Chart.js CDN)
3. Clear browser cache
4. Refresh page

### Data Not Updating
1. Check database for new records
2. Verify date calculations
3. Restart Django server
4. Check for JavaScript errors

### CSV Downloads Failing
1. Check file permissions
2. Verify URL patterns
3. Check server logs
4. Ensure data exists

### Performance Issues
1. Limit data range
2. Add database indexes
3. Check server resources
4. Optimize queries

## 📱 Mobile Usage

### Responsive Features
- **Single Column**: Automatic on mobile
- **Touch Friendly**: Large buttons and touch targets
- **Optimized Charts**: Scaled for mobile screens
- **Swipe Navigation**: Touch gestures supported

### Mobile Tips
- **Landscape Mode**: Better for charts
- **Pinch to Zoom**: Available on charts
- **Download**: CSV files work on mobile
- **Bookmark**: Save dashboard URL

## 🔒 Security Features

### Authentication
- **Login Required**: All analytics require authentication
- **Session Management**: Secure session handling
- **Device Ownership**: Users see only their data

### Data Protection
- **XSS Prevention**: All data properly escaped
- **CSRF Protection**: Token-based protection
- **Input Validation**: All inputs sanitized
- **SQL Injection**: ORM-based protection

## 📞 Support

### Contact Information
- **Email**: contact@vision072025@gmail.com
- **WhatsApp**: +254 702 715070
- **Documentation**: Full docs in `ANALYTICS_DASHBOARD_DOCUMENTATION.md`

### Common Issues
- **Charts Blank**: Check JavaScript console
- **Slow Loading**: Check database performance
- **Export Errors**: Verify file permissions
- **Mobile Issues**: Use landscape mode

## 🚀 Advanced Features

### Real-time Updates
```javascript
// Update charts with new data
window.updateAnalyticsCharts(newWaterData, newPowerData, newRuntimeData);
```

### Custom Date Ranges
- **Current**: Last 30 days
- **Monthly**: Last 12 months
- **Yearly**: Last 3 years
- **Custom**: Contact support for custom ranges

### Data Export Formats
- **CSV**: Comma-separated values
- **Future**: PDF, Excel (planned)
- **API**: REST endpoints (planned)

---

**Quick Access**: Bookmark `/AquaSavvy-Control/dashboard/device/analytics/`
**Last Updated**: January 2025
**Version**: 2.0
