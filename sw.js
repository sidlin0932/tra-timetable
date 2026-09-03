// Service Worker for 2026 台鐵時刻表 PWA (v3.9.43)
const CACHE_NAME = 'tra-timetable-pwa-v3.9.43';
const RUNTIME_CACHE = 'tra-runtime-v3.9.43';

// Core Application Shell & Timetable Data Assets
const CORE_ASSETS = [
  './',
  './index.html',
  './lite.html',
  './data.js',
  './full_network_timetable.json',
  './manifest.json',
  './icon-192.png',
  './icon-512.png'
];

// 1. Install: Pre-cache all critical assets immediately & skip waiting
self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW] Pre-caching core app assets for offline use (v3.9.43)...');
      return cache.addAll(CORE_ASSETS);
    })
  );
});

// 2. Activate: Clean up old version caches immediately and claim clients
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((name) => {
          if (name !== CACHE_NAME && name !== RUNTIME_CACHE) {
            console.log('[SW] Deleting obsolete cache:', name);
            return caches.delete(name);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// 3. Fetch Strategy: Cache-First for static assets & Stale-While-Revalidate with network fallback
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Ignore cross-origin non-GET requests
  if (event.request.method !== 'GET') return;

  // Handle local resources
  event.respondWith(
    caches.match(event.request, { ignoreSearch: true }).then((cachedResponse) => {
      if (cachedResponse) {
        // Fetch background update for dynamic data files if online
        if (url.pathname.endsWith('full_network_timetable.json') || url.pathname.endsWith('data.js')) {
          fetch(event.request).then((networkResponse) => {
            if (networkResponse && networkResponse.status === 200) {
              caches.open(CACHE_NAME).then((cache) => cache.put(event.request, networkResponse));
            }
          }).catch(() => {});
        }
        return cachedResponse;
      }

      // Network Fallback with Runtime Cache
      return fetch(event.request).then((networkResponse) => {
        if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
          return networkResponse;
        }

        const responseToCache = networkResponse.clone();
        caches.open(RUNTIME_CACHE).then((cache) => {
          cache.put(event.request, responseToCache);
        });

        return networkResponse;
      }).catch(() => {
        // Offline Fallback for HTML documents
        if (event.request.headers.get('accept') && event.request.headers.get('accept').includes('text/html')) {
          if (url.pathname.includes('lite')) {
            return caches.match('./lite.html', { ignoreSearch: true });
          }
          return caches.match('./index.html', { ignoreSearch: true });
        }
      });
    })
  );
});
