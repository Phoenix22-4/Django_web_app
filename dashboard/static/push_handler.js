// Minimal FCM push registration helper
// You must include Firebase SDK and your config snippet in the HTML before this runs.

async function registerPush() {
  if (!('Notification' in window)) return;
  const permission = await Notification.requestPermission();
  if (permission !== 'granted') return;

  if (!('serviceWorker' in navigator)) return;
  // Ensure service worker is registered at /static/sw.js
  const reg = await navigator.serviceWorker.register('/static/sw.js');

  if (!firebase?.messaging) return;
  const messaging = firebase.messaging();
  // v9 compat: ensure vapidKey is configured in Firebase console if needed
  const token = await messaging.getToken();
  if (!token) return;

  // Send token to backend
  const csrftoken = (document.cookie.split(';').find(c=>c.trim().startsWith('csrftoken='))||'').split('=')[1]||'';
  await fetch('/api/save_push_subscription/', {
    method: 'POST',
    headers: { 'X-CSRFToken': csrftoken },
    body: new URLSearchParams({ token })
  });
}

// Call this after login or on dashboard load
document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('enable-push');
  if (btn) btn.addEventListener('click', registerPush);
});

