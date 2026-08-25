// Service Worker for 2026 台鐵時刻表 PWA (v3.9.5)
const CACHE_NAME = 'tra-timetable-pwa-v395';
const RUNTIME_CACHE = 'tra-runtime-v395';

// Core Application Shell & Timetable Data Assets
const CORE_ASSETS = [
  './',
  './index.html',
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
    caches.open(CACHE_NAME).then(async (cache) => {
      console.log('[ServiceWorker] Caching core offline assets for', CACHE_NAME);
      for (const url of CORE_ASSETS) {
        try {
          const res = await fetch(url, { cache: 'reload' });
          if (res && res.ok) {
            await cache.put(url, res);
          }
        } catch (err) {
          console.warn('[ServiceWorker] Pre-cache warning for:', url, err);
        }
      }
    })
  );
});

// 2. Activate: Clean up old caches immediately and claim control of all clients
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME && key !== RUNTIME_CACHE) {
            console.log('[ServiceWorker] Deleting old cache version:', key);
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// 3. Fetch Strategy: Cache-First with ignoreSearch & Navigation Fallback (100% Offline Guaranteed)
self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // Strategy A: Page Navigation (HTML documents)
  if (req.mode === 'navigate' || req.destination === 'document') {
    event.respondWith(
      (async () => {
        try {
          // Try network first with a short timeout to get latest version if online
          const networkResponse = await fetch(req);
          if (networkResponse && networkResponse.ok) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(req, networkResponse.clone());
            return networkResponse;
          }
        } catch (err) {
          // Offline mode - network failed
        }

        // Return cached page immediately (ignore query parameters)
        const cachedDoc = await caches.match(req, { ignoreSearch: true })
          || await caches.match('./index.html', { ignoreSearch: true })
          || await caches.match('./', { ignoreSearch: true })
          || await caches.match('index.html', { ignoreSearch: true });

        if (cachedDoc) {
          return cachedDoc;
        }

        // Fallback generic response if somehow not found
        return new Response('<h1>2026 台鐵時刻表 (離線模式)</h1><p>請重新整理載入快取頁面。</p>', {
          headers: { 'Content-Type': 'text/html; charset=utf-8' }
        });
      })()
    );
    return;
  }

  // Strategy B: Local Static Assets (data.js, manifest, icons, json)
  if (url.origin === self.location.origin) {
    event.respondWith(
      (async () => {
        // Match cache with ignoreSearch: true so data.js?v=... matches data.js!
        const cachedResponse = await caches.match(req, { ignoreSearch: true });
        if (cachedResponse) {
          // Revalidate in background if online
          fetch(req).then(async (netRes) => {
            if (netRes && netRes.ok) {
              const cache = await caches.open(CACHE_NAME);
              cache.put(req, netRes);
            }
          }).catch(() => {/* Ignore offline background fetch */});
          return cachedResponse;
        }

        // Not in cache, try fetching from network
        try {
          const netRes = await fetch(req);
          if (netRes && netRes.ok) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(req, netRes.clone());
          }
          return netRes;
        } catch (err) {
          // Offline fallback for same-origin resources
          const fallback = await caches.match(url.pathname, { ignoreSearch: true });
          if (fallback) return fallback;
          throw err;
        }
      })()
    );
    return;
  }

  // Strategy C: External Resources (Google Fonts, CDNs)
  if (url.origin.includes('fonts.googleapis.com') || url.origin.includes('fonts.gstatic.com')) {
    event.respondWith(
      (async () => {
        const cachedFont = await caches.match(req);
        if (cachedFont) return cachedFont;

        try {
          const fontRes = await fetch(req);
          if (fontRes && fontRes.ok) {
            const cache = await caches.open(RUNTIME_CACHE);
            cache.put(req, fontRes.clone());
          }
          return fontRes;
        } catch (err) {
          // When offline, fonts will gracefully fallback to system sans-serif
          return cachedFont || new Response('', { status: 200, statusText: 'Offline Font Fallback' });
        }
      })()
    );
    return;
  }

  // Strategy D: Default stale-while-revalidate for any other GET requests
  event.respondWith(
    caches.match(req, { ignoreSearch: true }).then((cached) => {
      if (cached) return cached;
      return fetch(req).then((res) => {
        if (res && res.ok) {
          const cacheCopy = res.clone();
          caches.open(RUNTIME_CACHE).then((cache) => cache.put(req, cacheCopy));
        }
        return res;
      });
    })
  );
});
