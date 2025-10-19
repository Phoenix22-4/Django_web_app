// Simplified Push Notification Manager
class PushNotificationManager {
    constructor() {
        this.isSupported = 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window;
        this.init();
    }

    async init() {
        if (!this.isSupported) {
            console.log('Push notifications are not supported in this browser or environment.');
            return;
        }
        
        // Request permission immediately
        await this.requestPermission();
        
        // Register a dummy token or status to the server
        await this.sendTokenToServer();
    }

    async requestPermission() {
        try {
            const permission = await Notification.requestPermission();
            if (permission === 'granted') {
                console.log('Notification permission granted.');
                return true;
            } else {
                console.log('Notification permission denied.');
                return false;
            }
        } catch (error) {
            console.error('Error requesting notification permission:', error);
            return false;
        }
    }

    async sendTokenToServer() {
        try {
            const permission = Notification.permission;
            const response = await fetch('/api/register_fcm_token/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    fcm_token: permission === 'granted' ? 'browser_granted' : 'browser_denied',
                    enabled: permission === 'granted'
                })
            });

            const data = await response.json();
            if (data.status === 'success') {
                console.log('Notification preference registered successfully:', data.message);
            } else {
                console.error('Failed to register notification preference:', data.error);
            }
        } catch (error) {
            console.error('Error sending notification preference to server:', error);
        }
    }

    async testNotification() {
        if (Notification.permission === 'granted') {
            // Show local notification immediately
            this.showLocalNotification('Test Notification', 'This is a test notification from AquaSavvy!');
            
            // Also send to server for testing
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
                    console.log('Test notification sent successfully from server.');
                } else {
                    console.error('Failed to send test notification from server:', data.error);
                }
            } catch (error) {
                console.error('Error sending test notification to server:', error);
            }
        } else {
            alert('Please enable browser notifications to receive alerts.');
            this.requestPermission();
        }
    }

    showLocalNotification(title, body) {
        if (Notification.permission === 'granted') {
            const notification = new Notification(title, {
                body: body,
                icon: '/static/images/chat-icon.png',
                badge: '/static/images/chat-icon.png',
                tag: 'aquasavvy-notification',
                requireInteraction: true
            });

            notification.onclick = function() {
                window.focus();
                notification.close();
            };

            // Auto-close after 5 seconds
            setTimeout(() => {
                notification.close();
            }, 5000);
        }
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
}

// Initialize push notification manager
window.pushNotificationManager = new PushNotificationManager();