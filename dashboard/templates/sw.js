{% load static %} /** <--- ✅ FIX: Added this line **/
/*
 * AquaSavvy PWA Service Worker
 *
 * This file handles:
 * 1. Firebase Push Notifications
 * 2. Offline Caching (App Shell + Network/Cache strategies)
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
// Ensure the offline URL matches the one defined in dashboard/urls.py
const OFFLINE_URL = '{% url "offline_page" %}';
const APP_SHELL_URLS = [
    // Core pages - Adjust if your main entry point isn't '/' after login
    // '/', // Cache the public home if needed, or remove if PWA is login-only
    '{% url "login" %}', // Cache the login page
    '{% url "offline_page" %}', // The offline page itself

    // Static assets - Use the 'static' template tag
    '{% static "dashboard.css" %}',
    '{% static "aquasavvy-chat.css" %}',
    '{% static "aquasavvy-chat.js" %}',
    '{% static "push_handler.js" %}',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css',

    // Add paths to your icons - Crucial for manifest and notifications
    '{% static "icons/icon-192.png" %}',
    '{% static "icons/icon-512.png" %}',
    '{% static "icons/maskable-icon-512.png" %}'
];

// --- 3. Service Worker Event Listeners ---

// INSTALL: Cache the "App Shell" and core assets
self.addEventListener('install', (event) => {
  console.log('SW: Install event - Caching App Shell');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('SW: Caching:', APP_SHELL_URLS);
        // Filter out any potentially undefined URLs before caching
        const validUrlsToCache = APP_SHELL_URLS.filter(url => url && url !== 'None' && !url.includes('undefined'));
        if (validUrlsToCache.length !== APP_SHELL_URLS.length) {
            console.warn("SW: Some URLs were invalid and excluded from caching.");
        }
        return cache.addAll(validUrlsToCache);
      })
      .catch(err => {
        console.error('SW: App Shell caching failed severely.', err);
        // Log details to help diagnose which URL failed
        if (err instanceof TypeError && err.message.includes('addAll')) {
             console.error('Failed URLs list:', APP_SHELL_URLS);
        }
      })
      .then(() => {
          // Force the waiting service worker to become the active service worker.
          // This ensures the latest SW takes control immediately on activation.
          return self.skipWaiting();
      })
  );
});

// ACTIVATE: Clean up old caches and claim clients
self.addEventListener('activate', (event) => {
  console.log('SW: Activate event - Cleaning old caches');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter(name => name !== CACHE_NAME) // Delete caches that are not the current one
          .map(name => {
              console.log('SW: Deleting old cache:', name);
              return caches.delete(name);
          })
      );
    }).then(() => {
        // Claim clients immediately so the new SW controls the page without needing a refresh.
        console.log('SW: Claiming clients');
        return self.clients.claim();
    }).catch(err => {
        console.error('SW: Activation failed', err);
    })
  );
});

// FETCH: Intercept network requests using appropriate strategies
self.addEventListener('fetch', (event) => {
  const req = event.request;

  // --- Strategy: Network First, then Cache, then Offline Page (for HTML navigations) ---
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req)
        .then((networkResponse) => {
          console.log('SW: Serving navigate request from network:', req.url);
          // Clone the response to cache it safely
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(req, responseToCache);
          });
          return networkResponse;
        })
        .catch(() => {
          console.log('SW: Network failed for navigate request, trying cache:', req.url);
          // If network fails, serve from cache
          return caches.match(req)
            .then((cachedResponse) => {
              if (cachedResponse) {
                  console.log('SW: Serving navigate request from cache:', req.url);
                  return cachedResponse;
              }
              // If not in cache, return the offline page
              console.log('SW: Navigate request not in cache, serving offline page.');
              return caches.match(OFFLINE_URL).then(offlineResponse => {
                  if (!offlineResponse) {
                      console.error("SW: Offline page itself is not cached!");
                      // Fallback if offline page isn't cached
                      return new Response("<h1>Offline</h1><p>The app is offline and the requested page isn't cached. The offline fallback page is also missing.</p>", { headers: { 'Content-Type': 'text/html' }});
                  }
                  return offlineResponse;
              });
            });
        })
    );
    return; // Important: end execution for navigate requests here
  }

  // --- Strategy: Cache First, then Network (for static assets like CSS, JS, Images, Fonts) ---
  if (req.destination === 'style' || req.destination === 'script' || req.destination === 'image' || req.destination === 'font') {
     event.respondWith(
        caches.match(req)
          .then((cachedResponse) => {
            // Return from cache if found
            if (cachedResponse) {
              // console.log('SW: Serving asset from cache:', req.url); // Can be noisy, uncomment if needed
              return cachedResponse;
            }
            // Otherwise, fetch from network, cache, and return
            // console.log('SW: Asset not in cache, fetching from network:', req.url); // Can be noisy
            return fetch(req).then((networkResponse) => {
              // Check for valid response before caching
              if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
                  // Don't cache opaque responses or errors
                  return networkResponse;
              }
              const responseToCache = networkResponse.clone();
              caches.open(CACHE_NAME).then((cache) => {
                cache.put(req, responseToCache);
              });
              return networkResponse;
            });
          })
          .catch((err) => {
             console.warn('SW: Failed to fetch asset from network or cache:', req.url, err);
             // Provide a generic 404 response for failed assets
             return new Response(null, { status: 404 });
          })
     );
     return; // Important: end execution for asset requests here
  }

  // --- Default Strategy: Network Only (for API calls, etc.) ---
  // Don't cache API requests by default, as data might be stale.
  // If offline API behavior is needed, implement Background Sync or IndexedDB.
  // console.log('SW: Handling non-navigate/non-asset request via network:', req.url); // Can be noisy
  event.respondWith(fetch(req).catch(err => {
      console.error('SW: Network fetch failed for other request type:', req.url, err);
      // You could return a generic JSON error if it's an API call
      // return new Response(JSON.stringify({ error: 'Network error' }), { status: 503, headers: { 'Content-Type': 'application/json' }});
      // Or just let it fail naturally
  }));

});


// --- 4. Firebase Push Notification Handlers ---

self.addEventListener('push', function(event) {
  console.log('SW: Push received');
  let data = {};
  try {
      if (event.data) {
          data = event.data.json();
      } else {
          console.log('SW: Push event contained no data.');
      }
  }
  catch (e) { console.error("SW: Failed to parse push data json", e); }

  const title = data.title || 'AquaSavvy Solution';
  const body = data.body || 'You have a new notification';
  // Use the static tag for icon paths - ensure this resolves correctly
  const iconPath = '{% static "icons/icon-192.png" %}'; // Double-check this path
  const options = {
    body,
    icon: iconPath,
    badge: iconPath, // Badge is often monochrome, consider a separate badge icon
    // Ensure data is an object, default URL if none provided
    data: { url: data.url || '/' }
  };
  console.log('SW: Showing notification:', title, options);
  event.waitUntil(self.registration.showNotification(title, options)
    .catch(err => console.error('SW: Error showing notification:', err))
  );
});

self.addEventListener('notificationclick', function(event) {
  console.log('SW: Notification clicked:', event.notification.data);
  event.notification.close();
  // Ensure event.notification.data is accessed correctly
  const urlToOpen = event.notification.data && event.notification.data.url ? event.notification.data.url : '/';
  console.log('SW: Opening window:', urlToOpen);

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((windowClients) => {
      // Check if a window/tab matching the URL is already open.
      let clientIsFocused = false;
      for (let i = 0; i < windowClients.length; i++) {
        const client = windowClients[i];
        // Use endsWith or includes if the full URL might have query params etc.
        if (client.url.endsWith(urlToOpen) && 'focus' in client) {
          console.log('SW: Found existing window, focusing:', client.url);
          client.focus();
          clientIsFocused = true;
          break; // Exit loop once focused
        }
      }
      // If no window/tab is open or focused, open a new one.
      if (!clientIsFocused && clients.openWindow) {
        console.log('SW: No existing window found, opening new one:', urlToOpen);
        return clients.openWindow(urlToOpen)
            .catch(err => console.error('SW: Error opening window:', err));
      } else if (!clientIsFocused) {
          console.warn('SW: clients.openWindow is not supported.');
      }
    }).catch(err => console.error('SW: Error handling notification click:', err))
  );
});