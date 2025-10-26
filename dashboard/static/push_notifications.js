// Push Notifications JavaScript
// This file handles push notifications for the AquaGuard system
// CRITICAL: This script only runs on authenticated pages for security

console.log('Push notifications script loaded');

// Initialize push notifications when the page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔔 FCM: Push notifications initialized');
    
    // SECURITY GATE: Only initialize FCM token generation on authenticated pages
    if (window.user && window.user.isAuthenticated) {
        console.log('🔔 FCM: User is authenticated, initializing FCM token generation');
        console.log('🔔 FCM: User details - ID:', window.user.id, 'Username:', window.user.username);
        initializeFCMTokenGeneration();
    } else {
        console.log('🔔 FCM: User not authenticated, skipping FCM token generation for security');
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
                console.log('🔔 FCM: Registering service worker...');
                navigator.serviceWorker.register('/firebase-messaging-sw.js')
                    .then((registration) => {
                        console.log('✅ FCM: Service Worker registered successfully:', registration);
                        
                        // Request permission and get token (AUTHENTICATION GATE)
                        if ('Notification' in window) {
                            console.log('🔔 FCM: Notification API available, checking permission status...');
                            console.log('🔔 FCM: Current permission status:', Notification.permission);
                            
                            // GATED TOKEN GENERATION: Check permission status
                            if (Notification.permission === 'granted') {
                                console.log('🔔 FCM: Permission already granted - auto-generating token silently');
                                // Automatically and silently generate token
                                requestNotificationPermission(messaging);
                            } else if (Notification.permission === 'denied') {
                                console.log('🔔 FCM: Permission denied - showing in-app banner');
                                // Show non-intrusive banner instead of popup
                                showNotificationDeniedBanner();
                            } else {
                                console.log('🔔 FCM: Permission not determined - showing custom popup');
                                // Show custom popup for first-time users
                                showNotificationPermissionPopup(messaging);
                            }
                        } else {
                            console.log('❌ FCM: Notification API not available in this browser');
                        }
                    })
                    .catch((error) => {
                        console.error('❌ FCM: Service Worker registration failed:', error);
                    });
            } else {
                console.log('❌ FCM: Service Worker not supported in this browser');
            }

            // Handle foreground messages
            onMessage(messaging, (payload) => {
                console.log('📨 Message received:', payload);
                // Show notification
                if (payload.notification) {
                    showNotification(payload.notification.title, payload.notification.body, payload.notification.icon);
                }
            });
            
            // Confirmation log for background messages
            console.log('FCM is registered and token is ready for background messages.');
        });
    }).catch((error) => {
        console.error('❌ Error loading Firebase modules:', error);
    });
}

// Generate or retrieve device ID
function getDeviceId() {
    let deviceId = localStorage.getItem('fcm_device_id');
    if (!deviceId) {
        // Generate new UUID for device identification
        deviceId = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
        localStorage.setItem('fcm_device_id', deviceId);
        console.log('🔔 FCM: Generated new device ID:', deviceId);
    } else {
        console.log('🔔 FCM: Retrieved existing device ID:', deviceId);
    }
    return deviceId;
}

// Submit FCM token to Django backend with device ID
function submitFCMToken(token) {
    console.log('🔔 FCM: Submitting token to Django backend...');
    
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (!csrfToken) {
        console.error('❌ FCM: CSRF token not found - cannot submit token');
        return;
    }
    
    // Get or generate device ID
    const deviceId = getDeviceId();

    console.log('🔔 FCM: Sending POST request to /api/save_fcm_token/');
    fetch('/api/save_fcm_token/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ 
            token: token,
            device_id: deviceId
        })
    })
    .then(response => {
        console.log('🔔 FCM: Django response received:', response.status, response.statusText);
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            console.log('✅ SUCCESS: Token saved for User ID: ' + data.user_id + ' and Device ID: ' + deviceId);
        } else {
            console.error('❌ FCM: Token registration failed:', data.error);
        }
    })
    .catch(error => {
        console.error('❌ FCM: Error registering FCM token:', error);
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

// Show dismissible banner for denied notifications
function showNotificationDeniedBanner() {
    // Check if banner was already dismissed
    if (localStorage.getItem('notification_banner_dismissed') === 'true') {
        return;
    }
    
    const banner = document.createElement('div');
    banner.style.cssText = `
        position: fixed;
        top: 60px;
        right: 20px;
        background: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 8px;
        padding: 15px 20px;
        max-width: 350px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 9999;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    `;
    
    banner.innerHTML = `
        <div style="display: flex; align-items: start; gap: 10px;">
            <div style="font-size: 24px;">🔔</div>
            <div style="flex: 1;">
                <div style="font-weight: 600; color: #856404; margin-bottom: 5px;">Enable Notifications</div>
                <div style="font-size: 14px; color: #856404; line-height: 1.4;">
                    Stay updated with water alerts and pump status. Enable notifications in your browser settings.
                </div>
            </div>
            <button id="dismiss-banner" style="
                background: transparent;
                border: none;
                font-size: 20px;
                cursor: pointer;
                color: #856404;
                padding: 0;
                line-height: 1;
            ">×</button>
        </div>
    `;
    
    document.body.appendChild(banner);
    
    // Handle dismiss
    document.getElementById('dismiss-banner').onclick = () => {
        document.body.removeChild(banner);
        localStorage.setItem('notification_banner_dismissed', 'true');
    };
    
    // Auto-dismiss after 10 seconds
    setTimeout(() => {
        if (document.body.contains(banner)) {
            document.body.removeChild(banner);
        }
    }, 10000);
}

// Custom notification permission popup
function showNotificationPermissionPopup(messaging) {
    // Create a modal popup for notification permission
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    `;
    
    const popup = document.createElement('div');
    popup.style.cssText = `
        background: white;
        border-radius: 12px;
        padding: 30px;
        max-width: 400px;
        width: 90%;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    `;
    
    popup.innerHTML = `
        <div style="font-size: 48px; margin-bottom: 20px;">🔔</div>
        <h2 style="margin: 0 0 15px 0; color: #333; font-size: 24px;">AquaSavvy wants to show notifications</h2>
        <p style="margin: 0 0 25px 0; color: #666; line-height: 1.5;">
            Stay updated with important alerts about your water management system, tank levels, and pump status.
        </p>
        <div style="display: flex; gap: 10px; justify-content: center;">
            <button id="allow-notifications" style="
                background: #007bff;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 500;
            ">Allow Notifications</button>
            <button id="deny-notifications" style="
                background: #6c757d;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 500;
            ">Not Now</button>
        </div>
    `;
    
    modal.appendChild(popup);
    document.body.appendChild(modal);
    
    // Handle button clicks
    document.getElementById('allow-notifications').onclick = () => {
        document.body.removeChild(modal);
        requestNotificationPermission(messaging);
    };
    
    document.getElementById('deny-notifications').onclick = () => {
        document.body.removeChild(modal);
        console.log('❌ User denied notification permission');
    };
}

// Request notification permission
function requestNotificationPermission(messaging) {
    console.log('🔔 FCM: Requesting notification permission from browser...');
    Notification.requestPermission().then((permission) => {
        console.log('🔔 FCM: Permission result received:', permission);
        
        if (permission === 'granted') {
            console.log('✅ FCM: Notification permission granted by user');
            
            console.log('🔔 FCM: Generating FCM token...');
            // Import getToken from Firebase messaging
            import('https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging.js').then(({ getToken }) => {
                getToken(messaging, { 
                    vapidKey: window.firebaseConfig?.vapidKey || "{{ vapid_public_key|escapejs }}"
                }).then((currentToken) => {
                    if (currentToken) {
                        console.log('✅ FCM: Token generated and sent to Django');
                        console.log('📱 FCM: Token preview:', currentToken.substring(0, 20) + '...');
                        // Send token to Django backend with automatic registration
                        submitFCMToken(currentToken);
                    } else {
                        console.log('❌ FCM: No FCM token available - this should not happen');
                    }
                }).catch((err) => {
                    console.error('❌ FCM: Error getting FCM token:', err);
                });
            });
        } else {
            console.log('❌ FCM: Notification permission denied by user:', permission);
            // Show banner for denied permission
            showNotificationDeniedBanner();
        }
    });
}

// Export for use in other scripts
window.showNotification = showNotification;