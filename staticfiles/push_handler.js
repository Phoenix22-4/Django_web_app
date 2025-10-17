// Minimal FCM push registration helper
// You must include Firebase SDK and your config snippet in the HTML before this runs.

async function registerPush() {
  if (!('serviceWorker' in navigator) || !('Notification' in window) || !firebase?.messaging) {
    console.error('Push notifications are not supported by this browser.');
    return;
  }

  const permission = await Notification.requestPermission();
  if (permission !== 'granted') {
    console.log('Notification permission denied.');
    return;
  }

  try {
    // Register service worker from ROOT path
    const reg = await navigator.serviceWorker.register('/sw.js');
    console.log('Service Worker registered successfully.');

    const messaging = firebase.messaging();
    const vapidKey = 'BMLnBIiNgOMINbDOGA24NWnufsGSMP9GF-Z12V8dbEXA8NwBy-UFPOrF8kDpGdVjeIQsMRE-oxf-y60W1p4DEcY';
    const token = await messaging.getToken({ vapidKey, serviceWorkerRegistration: reg });
    if (!token) {
      console.error('Could not get push token.');
      return;
    }
    console.log('FCM Token:', token);

    // Get CSRF from hidden input
    const csrfEl = document.querySelector('[name=csrfmiddlewaretoken]');
    const csrftoken = csrfEl ? csrfEl.value : '';

    await fetch('/api/save_push_subscription/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': csrftoken
      },
      body: new URLSearchParams({ token })
    });

    console.log('Token sent to server.');
    alert('Notifications enabled!');
  } catch (error) {
    console.error('Push registration failed:', error);
  }
}

// Call this after login or on dashboard load
document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('enable-push');
  if (btn) btn.addEventListener('click', registerPush);
});

