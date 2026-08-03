const CACHE_NAME = 'devforge-cache-v1';
const ASSETS_TO_CACHE = [
    '/dashboard/'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS_TO_CACHE).catch(err => {
                console.log('Failed to precache: ', err);
            });
        })
    );
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cache) => {
                    if (cache !== CACHE_NAME) {
                        return caches.delete(cache);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

self.addEventListener('fetch', (event) => {
    const req = event.request;
    const url = new URL(req.url);

    // Only intercept local GET requests
    if (url.origin !== self.location.origin || req.method !== 'GET') {
        return;
    }

    // Ignore admin, API, WebSockets, payments, and AI requests
    if (url.pathname.startsWith('/admin/') || 
        url.pathname.startsWith('/api/') || 
        url.pathname.startsWith('/ws/') ||
        url.pathname.startsWith('/payments/') ||
        url.pathname.startsWith('/ai/')) {
        return;
    }

    // Cache-first for static files, Network-first for dynamic content
    if (url.pathname.startsWith('/static/')) {
        event.respondWith(
            caches.match(req).then((cachedResponse) => {
                if (cachedResponse) {
                    return cachedResponse;
                }
                return fetch(req).then((networkResponse) => {
                    if (networkResponse && networkResponse.status === 200) {
                        const responseToCache = networkResponse.clone();
                        caches.open(CACHE_NAME).then((cache) => {
                            cache.put(req, responseToCache);
                        });
                    }
                    return networkResponse;
                });
            })
        );
    } else {
        // Network-first strategy
        event.respondWith(
            fetch(req)
                .then((networkResponse) => {
                    if (networkResponse && networkResponse.status === 200) {
                        const responseToCache = networkResponse.clone();
                        caches.open(CACHE_NAME).then((cache) => {
                            cache.put(req, responseToCache);
                        });
                    }
                    return networkResponse;
                })
                .catch(() => {
                    return caches.match(req);
                })
        );
    }
});
