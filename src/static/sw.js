const CACHE_NAME = 'tryag-v2';
const OFFLINE_URL = 'app/static/offline.html';

const ASSETS_TO_CACHE = [
    OFFLINE_URL,
    'app/static/css/offline.css',
    'app/static/js/offline_db.js',
    'app/static/manifest.json',
    'app/static/icons/icon-192x192.png',
    'app/static/icons/icon-512x512.png',
    'app/static/icons/logo.png',
    'app/static/js/push_notifications.js'
];

// Install Event: Cache static assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS_TO_CACHE);
        })
    );
    self.skipWaiting();
});

// Activate Event: Clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// Fetch Event
self.addEventListener('fetch', (event) => {
    // Skip cross-origin requests
    if (!event.request.url.startsWith(self.location.origin)) return;

    // Strategy: Stale-While-Revalidate for static assets (icons, css, js)
    if (event.request.url.includes('/app/static/')) {
        event.respondWith(
            caches.open(CACHE_NAME).then((cache) => {
                return cache.match(event.request).then((cachedResponse) => {
                    const fetchPromise = fetch(event.request).then((networkResponse) => {
                        cache.put(event.request, networkResponse.clone());
                        return networkResponse;
                    });
                    return cachedResponse || fetchPromise;
                });
            })
        );
        return;
    }

    // Strategy: Network First, then Cache, then Offline Page for everything else (HTML)
    event.respondWith(
        fetch(event.request)
            .then((response) => {
                return response;
            })
            .catch(() => {
                return caches.match(event.request).then((cachedResponse) => {
                    if (cachedResponse) {
                        return cachedResponse;
                    }
                    if (event.request.mode === 'navigate') {
                        return caches.match(OFFLINE_URL);
                    }
                });
            })
    );
});

// Evento Push (Notificaciones)
self.addEventListener('push', function (event) {
    if (event.data) {
        const data = event.data.json();
        console.log('Push received:', data);

        const options = {
            body: data.body,
            icon: data.icon || 'app/static/icons/icon-192x192.png',
            badge: data.badge || 'app/static/icons/badge.png',
            data: {
                url: data.url || '/'
            }
        };

        event.waitUntil(
            self.registration.showNotification(data.title, options)
        );
    }
});

// Click en notificación
self.addEventListener('notificationclick', function (event) {
    console.log('Notification click received.');
    event.notification.close();

    event.waitUntil(
        clients.openWindow(event.notification.data.url)
    );
});
