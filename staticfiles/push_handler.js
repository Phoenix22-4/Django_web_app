// Push Handler JavaScript
// This file handles push notification events and Firebase messaging

console.log('Push handler script loaded');

// Initialize Firebase messaging when the page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Push handler initialized');
    
    // Check if Firebase is available
    if (typeof firebase !== 'undefined' && firebase.messaging) {
        console.log('Firebase messaging available');
        
        // Get the messaging instance
        const messaging = firebase.messaging();
        
        // Handle background messages
        messaging.onBackgroundMessage(function(payload) {
            console.log('Background message received:', payload);
            
            const notificationTitle = payload.notification.title;
            const notificationOptions = {
                body: payload.notification.body,
                icon: payload.notification.icon || '/static/images/logo.png'
            };
            
            return self.registration.showNotification(notificationTitle, notificationOptions);
        });
        
        // Handle foreground messages
        messaging.onMessage(function(payload) {
            console.log('Foreground message received:', payload);
            
            // Show notification in the foreground
            if (window.showNotification) {
                window.showNotification(
                    payload.notification.title,
                    payload.notification.body,
                    payload.notification.icon
                );
            }
        });
        
    } else {
        console.log('Firebase messaging not available');
    }
});