// Push Notifications JavaScript
// This file handles push notifications for the AquaGuard system
// CRITICAL: This script only runs on authenticated pages for security

console.log('Push notifications script loaded');

// Initialize push notifications when the page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Push notifications initialized');
    
    // Only initialize FCM token generation on authenticated pages
    if (window.user && window.user.isAuthenticated) {
        console.log('User is authenticated, initializing FCM token generation');
        initializeFCMTokenGeneration();
    } else {
        console.log('User not authenticated, skipping FCM token generation');
    }
});

// Initialize FCM token generation (only for authenticated users)
function initializeFCMTokenGeneration() {
    // Import Firebase modules dynamically
    import('https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js').then(({ initializeApp }) => {
        return import('https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging.js').then(({ getMessaging, getToken, onMessage }) => {
            
            // Firebase configuration (these values should be passed from Django template)
            const firebaseConfig = {
                apiKey: window.firebaseConfig?.apiKey || "{{ firebase_api_key|escapejs }}",
                authDomain: window.firebaseConfig?.authDomain || "{{ firebase_project_id|escapejs }}.firebaseapp.com",
                projectId: window.firebaseConfig?.projectId || "{{ firebase_project_id|escapejs }}",
                storageBucket: window.firebaseConfig?.storageBucket || "{{ firebase_project_id|escapejs }}.appspot.com",
                messagingSenderId: window.firebaseConfig?.messagingSenderId || "{{ firebase_messaging_sender_id|escapejs }}",
                appId: window.firebaseConfig?.appId || "{{ firebase_app_id|escapejs }}"
            };

            const app = initializeApp(firebaseConfig);
            const messaging = getMessaging(app);

            // Register service worker first
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/firebase-messaging-sw.js')
                    .then((registration) => {
                        console.log('✅ Service Worker registered:', registration);
                        
                        // Request permission and get token (AUTHENTICATION GATE)
                        if ('Notification' in window) {
                            Notification.requestPermission().then((permission) => {
                                if (permission === 'granted') {
                                    console.log('✅ Notification permission granted');
                                    
                                    getToken(messaging, { 
                                        vapidKey: window.firebaseConfig?.vapidKey || "{{ vapid_public_key|escapejs }}"
                                    }).then((currentToken) => {
                                        if (currentToken) {
                                            console.log('📱 FCM Token generated:', currentToken);
                                            // Send token to Django backend with automatic registration
                                            submitFCMToken(currentToken);
                                        } else {
                                            console.log('❌ No FCM token available');
                                        }
                                    }).catch((err) => {
                                        console.error('❌ Error getting FCM token:', err);
                                    });
                                } else {
                                    console.log('❌ Notification permission denied:', permission);
                                }
                            });
                        }
                    })
                    .catch((error) => {
                        console.error('❌ Service Worker registration failed:', error);
                    });
            }

            // Handle foreground messages
            onMessage(messaging, (payload) => {
                console.log('📨 Message received:', payload);
                // Show notification
                if (payload.notification) {
                    showNotification(payload.notification.title, payload.notification.body, payload.notification.icon);
                }
            });
        });
    }).catch((error) => {
        console.error('❌ Error loading Firebase modules:', error);
    });
}

// Submit FCM token to Django backend
function submitFCMToken(token) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (!csrfToken) {
        console.error('❌ CSRF token not found');
        return;
    }

    fetch('/api/save_fcm_token/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ token: token })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log('✅ FCM token registered successfully for user #' + data.special_user_number);
        } else {
            console.error('❌ FCM token registration failed:', data.error);
        }
    })
    .catch(error => {
        console.error('❌ Error registering FCM token:', error);
    });
}

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