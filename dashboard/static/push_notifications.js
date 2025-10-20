// Push Notifications JavaScript
// This file handles push notifications for the AquaGuard system

console.log('Push notifications script loaded');

// Initialize push notifications when the page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Push notifications initialized');
    
    // Check if the browser supports notifications
    if ('Notification' in window) {
        console.log('Browser supports notifications');
        
        // Request permission for notifications
        if (Notification.permission === 'default') {
            Notification.requestPermission().then(function(permission) {
                console.log('Notification permission:', permission);
            });
        }
    } else {
        console.log('Browser does not support notifications');
    }
});

// Function to show a notification
function showNotification(title, body, icon) {
    if ('Notification' in window && Notification.permission === 'granted') {
        const notification = new Notification(title, {
            body: body,
            icon: icon || '/static/images/logo.png'
        });
        
        // Auto-close after 5 seconds
        setTimeout(() => {
            notification.close();
        }, 5000);
        
        return notification;
    }
}

// Export for use in other scripts
window.showNotification = showNotification;