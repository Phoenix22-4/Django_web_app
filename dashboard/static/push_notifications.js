// dashboard/static/push_notifications.js
class PushNotificationManager {
    constructor() {
        this.isSupported = 'serviceWorker' in navigator && 'PushManager' in window;
        this.registration = null;
        this.init();
    }

    async init() {
        if (!this.isSupported) {
            console.log('Push notifications are not supported in this browser');
            return;
        }

        try {
            // Register service worker
            this.registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js');
            console.log('Service Worker registered successfully');

            // Request notification permission
            await this.requestPermission();

            // Get FCM token and register it
            await this.registerFCMToken();

        } catch (error) {
            console.error('Error initializing push notifications:', error);
        }
    }

    async requestPermission() {
        try {
            const permission = await Notification.requestPermission();
            
            if (permission === 'granted') {
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

    async registerFCMToken() {
        try {
            // Check if Firebase is available
            if (typeof firebase === 'undefined') {
                console.log('Firebase not loaded, skipping FCM token registration');
                return;
            }

            // Initialize Firebase
            const firebaseConfig = {
                apiKey: "your-api-key",
                authDomain: "your-project.firebaseapp.com",
                projectId: "your-project-id",
                storageBucket: "your-project.appspot.com",
                messagingSenderId: "123456789",
                appId: "your-app-id"
            };

            if (!firebase.apps.length) {
                firebase.initializeApp(firebaseConfig);
            }

            const messaging = firebase.messaging();

            // Get FCM token
            const token = await messaging.getToken({
                vapidKey: 'your-vapid-key' // Optional: Add VAPID key for web push
            });

            if (token) {
                console.log('FCM Token:', token);
                
                // Send token to server
                await this.sendTokenToServer(token);
                
                // Listen for token refresh
                messaging.onTokenRefresh(async () => {
                    const newToken = await messaging.getToken();
                    console.log('FCM Token refreshed:', newToken);
                    await this.sendTokenToServer(newToken);
                });

            } else {
                console.log('No FCM token available');
            }

        } catch (error) {
            console.error('Error registering FCM token:', error);
        }
    }

    async sendTokenToServer(token) {
        try {
            const response = await fetch('/api/register_fcm_token/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    fcm_token: token
                })
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                console.log('FCM token registered successfully');
            } else {
                console.error('Failed to register FCM token:', data.error);
            }
        } catch (error) {
            console.error('Error sending FCM token to server:', error);
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
            } else {
                console.error('Failed to send test notification:', data.error);
            }
        } catch (error) {
            console.error('Error sending test notification:', error);
        }
    }

    // Show local notification (fallback)
    showLocalNotification(title, body, icon = '/static/images/chat-icon.png') {
        if (Notification.permission === 'granted') {
            const notification = new Notification(title, {
                body: body,
                icon: icon,
                badge: icon,
                tag: 'aquasavvy-notification',
                requireInteraction: true,
                actions: [
                    {
                        action: 'view',
                        title: 'View Dashboard'
                    },
                    {
                        action: 'dismiss',
                        title: 'Dismiss'
                    }
                ]
            });

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
        }
    }

    // Handle notification click
    handleNotificationClick(event) {
        event.notification.close();
        
        if (event.action === 'view') {
            // Open dashboard
            event.waitUntil(
                clients.openWindow('/devices/')
            );
        } else if (event.action === 'dismiss') {
            // Just close the notification
            return;
        } else {
            // Default action - open the app
            event.waitUntil(
                clients.openWindow('/')
            );
        }
    }
}

// Initialize push notification manager when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.pushNotificationManager = new PushNotificationManager();
});

// Handle service worker messages
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.addEventListener('message', (event) => {
        const data = event.data;
        
        if (data.type === 'NOTIFICATION_CLICK') {
            // Handle notification click
            if (data.action === 'view') {
                window.location.href = '/devices/';
            }
        }
    });
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PushNotificationManager;
}
