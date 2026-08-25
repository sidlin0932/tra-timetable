// Service Worker for 2026 台鐵時刻表 PWA (v3.8.9)
const CACHE_NAME = 'tra-timetable-pwa-v389';
const LOCAL_ASSETS = [
  './',
  './index.html',
  './data.js',
  './manifest.json',
  './icon-192.png',
  './icon-512.png'
];

// Install: Cache all core application shell and timetable data assets safely
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(async (cache) => {
      console.log('[ServiceWorker] Pre-caching local offline assets');
      // Cache local files safely one by one to avoid total failure
      for (const url of LOCAL_ASSETS) {
        try {
          await cache.add(url);
        } catch (err) {
          console.warn('[ServiceWorker] Failed to cache:', url, err);
        }
      }
    }).then(() => self.skipWaiting())
  );
});

// Activate: Clean up older cache versions immediately
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keyList) => {
      return Promise.all(
        keyList.map((key) => {
          if (key !== CACHE_NAME) {
            console.log('[ServiceWorker] Removing old cache', key);
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch: Stale-while-revalidate / Cache-First strategy for ultra-fast offline experience
self.addEventListener('fetch', (event) => {
  // Only handle GET requests
  if (event.request.method !== 'GET') return;

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        // Return cached immediately, fetch update in background if online
        fetch(event.request).then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, networkResponse.clone());
            });
          }
        }).catch(() => {
          // Offline mode - ignore network fetch errors
        });
        return cachedResponse;
      }

      // If not in cache, fetch from network and cache
      return fetch(event.request).then((networkResponse) => {
        if (!networkResponse || networkResponse.status !== 200) {
          return networkResponse;
        }
        const responseToCache = networkResponse.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });
        return networkResponse;
      }).catch(() => {
        // If offline and request is for page navigation, return index.html
        if (event.request.mode === 'navigate' || event.request.destination === 'document') {
          return caches.match('./index.html') || caches.match('./');
        }
      });
    })
  );
});
