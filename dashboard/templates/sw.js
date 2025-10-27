/*
 * AquaSavvy PWA Service Worker
 *
 * This file handles:
 * 1. Firebase Push Notifications
 * 2. Offline Caching (App Shell + Network-First strategy)
 */

// --- 1. Firebase Setup ---
// We import the scripts. They will be available in this worker's scope.
importScripts('https://www.gstatic.com/firebasejs/9.23.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.23.0/firebase-messaging-compat.js');

// Initialize Firebase with the keys injected by Django
// These template tags will be replaced by your `urls.py` view.
const firebaseConfig = {
  apiKey: "{{ firebase_api_key }}",
  authDomain: "{{ firebase_project_id }}.firebaseapp.com",
  projectId: "{{ firebase_project_id }}",
  storageBucket: "{{ firebase_project_id }}.appspot.com",
  messagingSenderId: "{{ firebase_messaging_sender_id }}",
  appId: "{{ firebase_app_id }}",
};

// Only initialize if it hasn't been already
if (!firebase.apps.length) {
  firebase.initializeApp(firebaseConfig);
}
const messaging = firebase.messaging();

// --- 2. PWA Caching Setup ---

const CACHE_NAME = 'aquasavvy-cache-v1';
const OFFLINE_URL = '/offline/'; // We will route this to your offline.html page
const APP_SHELL_URLS = [
    '/', // Your home page
    '/offline/', // The offline page itself
    // We get the static paths from Django's template engine
    // NOTE: This assumes your `dashboard.urls` has a URL named 'offline_page'
    // that points to the `offline.html` template.
    // If not, just cache 'offline.html' and we'll fetch it by name.
    // Let's keep it simple: we'll cache the static files.
    '{{ "dashboard.css"|static }}',
    '{{ "aquasavvy-chat.css"|static }}',
    '{{ "aquasavvy-chat.js"|static }}',
    '{{ "push_handler.js"|static }}',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css'
];

// --- 3. Service Worker Event Listeners ---

// INSTALL: Cache the "App Shell"
self.addEventListener('install', (event) => {
  console.log('SW: Install event');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('SW: Caching App Shell');
        // We also need to cache the offline.html template.
        // Let's add a specific URL for it in dashboard/urls.py
        // For now, let's assume you created a URL named 'offline_page'
        const urlsToCache = [
            ...APP_SHELL_URLS,
            '{% url "offline_page" %}' // Add this URL!
        ];
        return cache.addAll(urlsToCache);
      })
      .catch(err => {
        console.error('SW: App Shell caching failed', err);
      })
  );
  self.skipWaiting();
});

// ACTIVATE: Clean up old caches
self.addEventListener('activate', (event) => {
  console.log('SW: Activate event');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter(name => name !== CACHE_NAME)
          .map(name => caches.delete(name))
      );
    })
  );
  return self.clients.claim();
});

// FETCH: Intercept network requests
self.addEventListener('fetch', (event) => {
  const req = event.request;
  
  // We only cache GET requests
  if (req.method !== 'GET') {
    event.respondWith(fetch(req));
    return;
  }
  
  // Strategy: Network First, then Cache, then Offline Page
  event.respondWith(
    fetch(req)
      .then((networkResponse) => {
        // If request is successful, cache it and return it
        const responseToCache = networkResponse.clone();
        caches.open(CACHE_NAME).then((cache) => {
          // Don't cache admin, auth, or API requests that change data
          if (!req.url.includes('/admin') && !req.url.includes('/api') && !req.url.includes('/accounts')) {
             cache.put(req, responseToCache);
          }
        });
        return networkResponse;
      })
      .catch(() => {
        // If network fails (offline), try to get from cache
        return caches.match(req)
          .then((cachedResponse) => {
            if (cachedResponse) {
              return cachedResponse; // Return from cache
            }
            // If not in cache and it's a page navigation, show offline page
            if (req.mode === 'navigate') {
              return caches.match('{% url "offline_page" %}');
            }
            // For other assets (images, etc.), just fail
            return new Response(null, { status: 404 });
          });
      })
  );
});


// --- 4. Firebase Push Notification Handlers (Your existing code) ---

self.addEventListener('push', function(event) {
  console.log('SW: Push received');
  let data = {};
  try { data = event.data.json(); } catch (e) {}
  
  const title = data.title || 'AquaSavvy Solution';
  const body = data.body || 'You have a new notification';
  const options = {
    body,
    icon: '{{ "icons/icon-192.png"|static }}', // Use static path
    badge: '{{ "icons/icon-192.png"|static }}', // Use static path
    data: data.url || '/'
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', function(event) {
  console.log('SW: Notification clicked');
  event.notification.close();
  const url = event.notification.data || '/';
  event.waitUntil(clients.openWindow(url));
});