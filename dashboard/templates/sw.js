self.addEventListener('push', function(event) {
  let data = {};
  try { data = event.data.json(); } catch (e) {}
  const title = data.title || 'AquaSavvy Solution';
  const body = data.body || 'You have a new notification';
  const options = {
    body,
    icon: '/static/icon-192.png',
    badge: '/static/icon-192.png',
    data: data.url || '/'
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  const url = event.notification.data || '/';
  event.waitUntil(clients.openWindow(url));
});

