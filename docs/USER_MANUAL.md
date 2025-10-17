# AquaSavvy User Manual

## Welcome to AquaSavvy! 🌊

Your intelligent water management system that keeps your water supply monitored, controlled, and optimized 24/7 with advanced IoT integration, AI assistance, and push notifications.

## Quick Start Guide

### 1. **Accessing Your System**
- Open your web browser
- Navigate to your AquaSavvy dashboard
- Login with your credentials
- You'll see your device list or dashboard

### 2. **Understanding the Dashboard**

#### **Header Section**
- **System Name**: Shows your device name (e.g., "AquaSavvy: Main Tank")
- **Connection Status**: 
  - 🟢 Green = Connected to AWS IoT
  - 🔴 Red = Disconnected
  - 🟡 Yellow = Connecting

#### **Main Dashboard Grid**

**Left Side - Charts (Light Blue Cards)**
- **Pump Runtime**: Shows how long your pump ran in the last 24 hours
- **Power Usage**: Displays electricity consumption for the same period

**Right Side - Tanks (Yellow Cards)**
- **Tank Levels**: Visual representation of your water tanks
- **Percentage**: Exact water level percentage
- **Status**: Dynamic tank support (1-4+ tanks automatically detected)

#### **Control Section (Bottom)**

**Pump Control**
- **Pump Icon**: Animated pump symbol showing system status
- **ON/OFF Buttons**: Manual pump control via AWS IoT commands
- **Status Display**: Current pump status and power consumption

**Status Messages**
- **Tank Levels**: Current percentage for each tank
- **System Alerts**: Any important notifications
- **AWS IoT Status**: Real-time connection to your devices

**Automation Timeslots**
- **4 Configurable Slots**: Set up automated rules
- **Plus Button**: Click to create new automation rules
- **Rule Management**: Save, delete, and activate rules
- **Real-time Execution**: Rules automatically control pump based on tank levels

### 3. **Using the AI Assistant** 🤖

#### **Accessing the Chat**
- Look for the blue chat button in the bottom-right corner
- Click to open the AI assistant powered by Google Gemini
- Type your questions about your water system

#### **What You Can Ask**
- "How do I check my tank levels?"
- "Why is my pump not working?"
- "How do I set up automation?"
- "What maintenance do I need to do?"
- "How do I troubleshoot connection issues?"
- "How do I configure AWS IoT settings?"
- "What are the power consumption patterns?"

#### **Getting Help**
- The AI knows your system inside and out
- Ask specific questions about your setup
- Get instant troubleshooting help
- Receive maintenance reminders
- Get AWS IoT configuration guidance

### 4. **Setting Up Automation**

#### **Creating a Rule**
1. Click the **+** button on any timeslot
2. Fill in the form:
   - **Rule Name**: e.g., "Night Refill"
   - **Start Time**: When to begin (e.g., 22:00)
   - **End Time**: When to stop (e.g., 06:00)
   - **Tank to Monitor**: Select which tank to watch
   - **Turn ON Below**: Minimum level (e.g., 30%)
   - **Turn OFF Above**: Maximum level (e.g., 80%)
3. Click **Save** to store the rule
4. Click **Activate** to make it active

#### **Managing Rules**
- **Save**: Store your rule configuration
- **Delete**: Remove a rule completely
- **Activate**: Make this rule active (only one can be active at a time)
- **Real-time Control**: Rules automatically send commands to your device via AWS IoT

### 5. **Understanding Tank Display**

#### **Visual Indicators**
- **Water Level**: Blue fill shows current tank level
- **Percentage**: Exact level displayed numerically
- **Tank Type**: Dynamic tank names (Overhead, Underground, Storage, etc.)

#### **Dynamic Layout**
- **1 Tank**: Single large display
- **2 Tanks**: Side-by-side layout
- **3 Tanks**: 2x2 grid with one empty space
- **4+ Tanks**: 2x2 grid, all spaces filled

### 6. **AWS IoT Integration** ☁️

#### **Real-time Data Reception**
- Your devices send data directly to AWS IoT Core
- Data is automatically processed and stored
- Real-time updates appear on your dashboard
- No manual refresh needed

#### **Device Commands**
- Manual pump control sends commands via AWS IoT
- Automation rules send commands automatically
- Device shadow maintains state synchronization
- Commands are queued and delivered reliably

#### **Connection Monitoring**
- AWS IoT connection status displayed in header
- Automatic reconnection if connection drops
- Error handling for network issues
- Real-time status updates

### 7. **Push Notifications** 📱

#### **Setting Up Notifications**
1. Allow notifications when prompted by your browser
2. Your FCM token is automatically registered
3. You'll receive a welcome notification
4. All alerts will be sent to your device

#### **Types of Notifications**
- **Tank Level Alerts**: Low/high water level warnings
- **Pump Status**: When pump starts/stops
- **System Alerts**: Connection issues or errors
- **Automation Updates**: Rule execution notifications
- **Welcome Messages**: After login

#### **Managing Notifications**
- Test notifications using the test button
- Notifications work even when browser is closed
- Click notifications to open dashboard
- Dismiss notifications manually

### 8. **Monitoring Your System**

#### **Real-time Updates**
- All data updates automatically via WebSocket
- No need to refresh the page
- AWS IoT provides reliable data delivery
- Push notifications keep you informed

#### **Status Indicators**
- **Connection Status**: Always visible in header
- **Pump Status**: Shows current operation
- **Tank Levels**: Live percentage updates
- **Power Usage**: Real-time consumption data
- **AWS IoT Status**: Cloud connection status

### 9. **Troubleshooting Common Issues**

#### **Connection Problems**
- Check your internet connection
- Look for red status indicators
- Verify AWS IoT credentials are configured
- Try refreshing the page
- Contact support if issues persist

#### **Pump Issues**
- Check power supply to pump
- Verify pump is not blocked
- Check AWS IoT command delivery
- Use AI assistant for specific help
- Check device shadow for last known state

#### **Tank Monitoring**
- Ensure sensors are clean
- Check for loose connections
- Verify tank is not empty
- Check AWS IoT data reception
- Contact support for sensor issues

#### **Push Notification Issues**
- Check browser notification permissions
- Verify FCM token registration
- Test notifications using test button
- Check Firebase configuration
- Contact support for persistent issues

### 10. **Mobile Usage**

#### **Responsive Design**
- Works on phones and tablets
- Touch-friendly interface
- Optimized for mobile viewing
- All features available on mobile
- Push notifications work on mobile

#### **Mobile Tips**
- Use landscape mode for better chart viewing
- Chat assistant works great on mobile
- Touch and hold for detailed information
- Swipe to navigate between sections
- Notifications open app automatically

### 11. **Getting Support**

#### **AI Assistant**
- Available 24/7 in the chat widget
- Ask specific questions about your system
- Get instant troubleshooting help
- Receive maintenance recommendations
- AWS IoT configuration assistance

#### **Contact Information**
- **Email**: contact:vision072025@gmail.com
- **WhatsApp**: +254 702 715070
- **AI Chat**: Use the blue chat button anytime

#### **Emergency Procedures**
- If system fails, check power and connections
- Manual pump override available via AWS IoT
- Emergency contact information in dashboard
- Backup procedures documented in system
- Device shadow maintains last known state

### 12. **Best Practices**

#### **Regular Monitoring**
- Check dashboard daily
- Monitor tank levels regularly
- Watch for unusual patterns
- Set up automation for convenience
- Review AWS IoT connection status

#### **Maintenance**
- Clean sensors monthly
- Check pump operation weekly
- Monitor power consumption
- Update system as needed
- Verify AWS IoT connectivity

#### **Automation Tips**
- Set realistic level thresholds
- Consider usage patterns
- Test automation rules
- Monitor performance regularly
- Use AWS IoT device shadow for debugging

#### **Security**
- Keep AWS IoT credentials secure
- Use strong passwords
- Enable two-factor authentication
- Regular security updates
- Monitor access logs

## Need More Help?

The AI assistant is always ready to help with specific questions about your system. Just click the chat button and ask away!

---

**AquaSavvy Solutions** - Making water management simple and intelligent with IoT and AI. 💧🤖☁️
