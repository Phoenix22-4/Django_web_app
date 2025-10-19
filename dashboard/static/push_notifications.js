// Simple Push Notification Manager for AquaSavvy
class PushNotificationManager {
    constructor() {
        this.isSupported = 'Notification' in window;
        this.permission = Notification.permission;
        this.init();
    }

    async init() {
        if (!this.isSupported) {
            console.log('Push notifications are not supported in this browser');
            return;
        }

        console.log('Push notification manager initialized');
        
        // Request permission if not already granted
        if (this.permission === 'default') {
            await this.requestPermission();
        }
    }

    async requestPermission() {
        try {
            this.permission = await Notification.requestPermission();
            
            if (this.permission === 'granted') {
                console.log('Notification permission granted');
                return true;
            } else {
                console.log('Notification permission denied');
                return false;
            }
        } catch (error) {
            console.error('Error requesting notification permission:', error);
            return false;
        }
    }

    showNotification(title, body, options = {}) {
        if (this.permission !== 'granted') {
            console.log('Notification permission not granted');
            return null;
        }

        const notificationOptions = {
            body: body,
            icon: '/static/images/chat-icon.png',
            badge: '/static/images/chat-icon.png',
            tag: 'aquasavvy-notification',
            requireInteraction: true,
            ...options
        };

        const notification = new Notification(title, notificationOptions);

        // Handle notification click
        notification.onclick = () => {
            window.focus();
            notification.close();
            // Navigate to dashboard
            window.location.href = '/devices/';
        };

        // Auto-close after 10 seconds
        setTimeout(() => {
            notification.close();
        }, 10000);

        return notification;
    }

    async testNotification() {
        try {
            const response = await fetch('/api/test_notification/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                console.log('Test notification sent successfully');
                // Show local notification as well
                this.showNotification(
                    'Test Notification',
                    'This is a test notification from AquaSavvy!',
                    { tag: 'test-notification' }
                );
            } else {
                console.error('Failed to send test notification:', data.error);
            }
        } catch (error) {
            console.error('Error sending test notification:', error);
        }
    }

    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }

    // Show system alerts
    showTankLevelAlert(tankName, level, alertType) {
        let title, body;
        
        if (alertType === 'low') {
            title = 'Low Water Level Alert';
            body = `Tank '${tankName}' is at ${level}% - below minimum threshold`;
        } else if (alertType === 'high') {
            title = 'High Water Level Alert';
            body = `Tank '${tankName}' is at ${level}% - above maximum threshold`;
        } else {
            title = 'Tank Level Alert';
            body = `Tank '${tankName}' is at ${level}%`;
        }

        this.showNotification(title, body, { tag: `tank-${tankName}-${alertType}` });
    }

    showPumpStatusAlert(pumpStatus, reason = null) {
        const title = pumpStatus ? 'Pump Started' : 'Pump Stopped';
        let body = `Pump has been turned ${pumpStatus ? 'ON' : 'OFF'}`;
        
        if (reason) {
            body += ` - ${reason}`;
        }

        this.showNotification(title, body, { tag: 'pump-status' });
    }

    showSystemAlert(alertType, message) {
        const title = `AquaSavvy System Alert - ${alertType}`;
        this.showNotification(title, message, { tag: `system-${alertType}` });
    }

    showWelcomeNotification() {
        this.showNotification(
            'Welcome to AquaSavvy!',
            'Your water management system is now connected. You\'ll receive alerts about your devices.',
            { tag: 'welcome' }
        );
    }
}

// Initialize push notification manager when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.pushNotificationManager = new PushNotificationManager();
    
    // Show welcome notification if this is the first visit
    const hasSeenWelcome = localStorage.getItem('aquasavvy-welcome-shown');
    if (!hasSeenWelcome && window.pushNotificationManager.permission === 'granted') {
        setTimeout(() => {
            window.pushNotificationManager.showWelcomeNotification();
            localStorage.setItem('aquasavvy-welcome-shown', 'true');
        }, 2000);
    }
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PushNotificationManager;
}