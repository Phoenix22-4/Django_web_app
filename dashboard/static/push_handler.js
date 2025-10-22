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
        
        // Only handle foreground messages in main thread
        // Background messages are handled by the service worker
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