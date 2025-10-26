// Push Notifications JavaScript
// This file handles push notifications for the AquaGuard system
// Uses Firebase Cloud Messaging (FCM) for web push notifications

console.log('Push notifications script loaded');

// Initialize push notifications when the page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔔 FCM: Push notifications script loaded');
    
    // Security check - only initialize if user is authenticated
    if (!window.user || !window.user.isAuthenticated) {
        console.log('🔔 FCM: User not authenticated, skipping FCM initialization');
        return;
    }
    
    console.log('🔔 FCM: User authenticated, checking for device ID...');
    
    // Get device ID from meta tag or data attribute
    const deviceIdElement = document.querySelector('[data-device-id]') || document.getElementById('device-id');
    const deviceId = deviceIdElement ? (deviceIdElement.getAttribute('data-device-id') || deviceIdElement.getAttribute('content')) : null;
    
    if (deviceId) {
        console.log('🔔 FCM: Device ID found:', deviceId);
        console.log('🔔 FCM: Initializing FCM for device:', deviceId);
        initializeFCMTokenGeneration(deviceId);
    } else {
        console.log('🔔 FCM: No device ID found, skipping FCM initialization');
    }
});

// Initialize FCM token generation
async function initializeFCMTokenGeneration(deviceId) {
    try {
        // Load Firebase SDK scripts
        await loadFirebaseSDK();
        
        // Firebase configuration from Django context (all values from environment variables)
        const firebaseConfig = {
            apiKey: window.firebaseConfig?.firebase_api_key || '',
            authDomain: window.firebaseConfig?.firebase_auth_domain || '',
            projectId: window.firebaseConfig?.firebase_project_id || '',
            storageBucket: window.firebaseConfig?.firebase_storage_bucket || '',
            messagingSenderId: window.firebaseConfig?.firebase_messaging_sender_id || '',
            appId: window.firebaseConfig?.firebase_app_id || '',
            measurementId: window.firebaseConfig?.firebase_measurement_id || ''
        };
        
        console.log('🔔 FCM: Firebase config:', firebaseConfig);
        
        // Check if required config is present
        const requiredKeys = ['apiKey', 'projectId', 'messagingSenderId', 'appId'];
        const missingKeys = requiredKeys.filter(key => !firebaseConfig[key]);
        
        if (missingKeys.length > 0) {
            console.error('❌ FCM: Missing required Firebase configuration:', missingKeys);
            console.error('❌ FCM: Please set the following environment variables:');
            missingKeys.forEach(key => {
                const envVar = key === 'apiKey' ? 'FIREBASE_WEB_API_KEY' :
                              key === 'messagingSenderId' ? 'FIREBASE_MESSAGING_SENDER_ID' :
                              key === 'appId' ? 'FIREBASE_WEB_APP_ID' : key.toUpperCase();
                console.error(`   - ${envVar}`);
            });
            return;
        }
        
        // Initialize Firebase using compat API
        firebase.initializeApp(firebaseConfig);
        const messaging = firebase.messaging();

        // Register service worker from ROOT path (critical for FCM)
        console.log('🔔 FCM: Registering service worker from root...');
        const registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js');
        console.log('✅ FCM: Service Worker registered successfully:', registration);
        
        // Check notification permission with improved logic
        const permissionStatus = Notification.permission;
        console.log(`🔔 FCM: Permission [${permissionStatus}] - ${permissionStatus === 'granted' ? 'Generating token...' : permissionStatus === 'denied' ? 'Blocked by user' : 'Will request permission'}`);
        
        if (permissionStatus === 'granted') {
            // Permission already granted, get token
            console.log('🔔 FCM: Permission already granted, generating token...');
            await generateAndSendToken(messaging, deviceId);
        } else if (permissionStatus === 'default') {
            // Ask for permission using custom popup for better UX
            console.log('🔔 FCM: Showing permission request...');
            showNotificationPermissionPopup(messaging, deviceId);
        } else {
            console.log('❌ FCM: Notifications blocked - showing info banner');
            showNotificationBlockedBanner();
        }
        
        // Handle foreground messages
        messaging.onMessage((payload) => {
            console.log('🔔 FCM: Message received in foreground:', payload);
            
            // Show notification even when app is in foreground
            if (Notification.permission === 'granted') {
                const notificationTitle = payload.notification?.title || 'AquaGuard Alert';
                // Use namespaced static paths for icons
                const notificationOptions = {
                    body: payload.notification?.body || 'You have a new notification',
                    icon: payload.notification?.icon || '/static/dashboard/images/chat-icon.png',
                    badge: '/static/dashboard/images/chat-icon.png',
                    data: payload.data
                };
                
                new Notification(notificationTitle, notificationOptions);
            }
        });
        
    } catch (error) {
        console.error('❌ FCM: Initialization failed:', error);
    }
}

// Load Firebase SDK scripts
async function loadFirebaseSDK() {
    // Load Firebase SDK using script tags for better compatibility
    return new Promise((resolve, reject) => {
        // Check if already loaded
        if (window.firebase && window.firebase.app && window.firebase.messaging) {
            console.log('🔔 FCM: Firebase SDK already loaded');
            resolve();
            return;
        }
        
        // Load Firebase App
        const appScript = document.createElement('script');
        appScript.src = 'https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js';
        appScript.onload = () => {
            // Load Firebase Messaging
            const messagingScript = document.createElement('script');
            messagingScript.src = 'https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js';
            messagingScript.onload = () => {
                console.log('✅ FCM: Firebase SDK loaded successfully');
                resolve();
            };
            messagingScript.onerror = reject;
            document.head.appendChild(messagingScript);
        };
        appScript.onerror = reject;
        document.head.appendChild(appScript);
    });
}

// Generate and send FCM token to Django backend
async function generateAndSendToken(messaging, deviceId) {
    try {
        // Get VAPID key from global variable set in base.html
        const vapidKey = window.firebaseVapiKey || '';
        
        if (!vapidKey) {
            console.error('❌ FCM: VAPID key is missing. Please set VAPID_PUBLIC_KEY environment variable.');
            console.error('❌ FCM: Get your VAPID key from Firebase Console → Project Settings → Cloud Messaging → Web Push certificates');
            return;
        }
        
        console.log('🔔 FCM: Getting token with VAPID key...');
        const token = await messaging.getToken({
            vapidKey: vapidKey
        });
        
        if (token) {
            console.log('✅ FCM: Token generated successfully');
            const userId = window.user?.id || 'unknown';
            console.log(`🔔 FCM: Token generated. Sending for user [${userId}]...`);
            console.log('📱 FCM: Token preview:', token.substring(0, 20) + '...');
            submitFCMToken(token, deviceId);
        } else {
            console.log('❌ FCM: No token available');
        }
    } catch (error) {
        console.error('❌ FCM: Error generating token:', error);
    }
}

// Submit FCM token to Django backend
function submitFCMToken(token, deviceId) {
    console.log('🔔 FCM: Submitting token to Django backend...');
    
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (!csrfToken) {
        console.error('❌ FCM: CSRF token not found - cannot submit token');
        return;
    }

    console.log('🔔 FCM: Sending POST request to /api/save_fcm_token/');
    console.log('🔔 FCM: Device ID:', deviceId);
    
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
            console.log('✅ FCM: Token registered successfully for user #' + data.special_user_number);
            console.log('✅ FCM: Token ID:', data.token_id);
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
            icon: icon || '/static/dashboard/images/chat-icon.png'
        });
        
        // Auto-close after 5 seconds
        setTimeout(() => {
            notification.close();
        }, 5000);
        
        return notification;
    }
}

// Custom notification permission popup
function showNotificationPermissionPopup() {
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
    document.getElementById('allow-notifications').onclick = async () => {
        document.body.removeChild(modal);
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
            console.log('✅ FCM: Permission granted by user');
            const deviceIdElement = document.querySelector('[data-device-id]') || document.getElementById('device-id');
            const deviceId = deviceIdElement ? (deviceIdElement.getAttribute('data-device-id') || deviceIdElement.getAttribute('content')) : null;
            if (deviceId && window.firebase) {
                const messaging = firebase.messaging();
                await generateAndSendToken(messaging, deviceId);
            }
        }
    };
    
    document.getElementById('deny-notifications').onclick = () => {
        document.body.removeChild(modal);
        console.log('❌ FCM: User dismissed in-app permission prompt');
    };
}

// Request notification permission
function requestNotificationPermission(triggerSource = 'auto') {
    console.log(`🔔 FCM: Requesting notification permission (source: ${triggerSource})...`);
    console.log('🔔 FCM: Permission panel shown. Awaiting browser response...');
    
    // Get device ID
    const deviceIdElement = document.querySelector('[data-device-id]') || document.getElementById('device-id');
    const deviceId = deviceIdElement ? (deviceIdElement.getAttribute('data-device-id') || deviceIdElement.getAttribute('content')) : null;

    Notification.requestPermission()
        .then((permission) => {
            console.log('🔔 FCM: Permission result received:', permission);

            if (permission === 'granted') {
                console.log('✅ FCM: Notification permission granted by user');
                if (deviceId) {
                    console.log('🔔 FCM: Reinitializing FCM to generate token...');
                    // Reinitialize FCM after permission granted
                    initializeFCMTokenGeneration(deviceId);
                } else {
                    console.error('❌ FCM: No device ID found');
                }
            } else {
                console.log('❌ FCM: Notification permission denied by user:', permission);
            }
        })
        .catch((err) => {
            console.error('❌ FCM: Error getting permission:', err);
        });
}

// Export for use in other scripts
window.showNotification = showNotification;