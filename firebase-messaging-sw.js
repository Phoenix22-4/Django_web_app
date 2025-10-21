// Firebase Service Worker for AquaSavvy
try {
    importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-app-compat.js');
    importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-messaging-compat.js');

    // Initialize Firebase
    firebase.initializeApp({
        apiKey: "your-api-key",
        authDomain: "your-project.firebaseapp.com",
        projectId: "your-project-id",
        storageBucket: "your-project.appspot.com",
        messagingSenderId: "123456789",
        appId: "your-app-id"
    });

    // Initialize Firebase Messaging
    const messaging = firebase.messaging();
} catch (error) {
    console.log('Firebase messaging not available in service worker context:', error);
}

// Handle background messages
try {
    if (typeof messaging !== 'undefined') {
        messaging.onBackgroundMessage(function(payload) {
            console.log('[firebase-messaging-sw.js] Received background message ', payload);
            
            const notificationTitle = payload.notification.title || 'AquaSavvy Notification';
            const notificationOptions = {
                body: payload.notification.body || 'You have a new notification',
                icon: '/static/images/chat-icon.png',
                badge: '/static/images/chat-icon.png',
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
            };

            self.registration.showNotification(notificationTitle, notificationOptions);
        });
    }
} catch (error) {
    console.log('Firebase messaging background handler not available:', error);
}

// Handle notification clicks
self.addEventListener('notificationclick', function(event) {
    console.log('[firebase-messaging-sw.js] Notification click received.');
    
    event.notification.close();
    
    if (event.action === 'view') {
        // Open the dashboard
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
});
