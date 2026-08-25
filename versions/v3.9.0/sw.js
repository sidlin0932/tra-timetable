// Service Worker for 2026 台鐵時刻表 PWA (v3.9.6)
const CACHE_NAME = 'tra-timetable-pwa-v396';
const RUNTIME_CACHE = 'tra-runtime-v396';

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

// 3. Fetch Strategy: Network-First when Online, Instant Cache Fallback when Offline
self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // Strategy A: Page Navigation & Core JS Data
  if (req.mode === 'navigate' || req.destination === 'document' || url.pathname.endsWith('index.html') || url.pathname.endsWith('data.js')) {
    event.respondWith(
      (async () => {
        try {
          // Network-first with fresh content
          const netRes = await fetch(req, { cache: 'no-cache' });
          if (netRes && netRes.ok) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(req, netRes.clone());
            return netRes;
          }
        } catch (err) {
          // Offline or network error -> fallback to cache
        }

        const cachedDoc = await caches.match(req, { ignoreSearch: true })
          || await caches.match('./index.html', { ignoreSearch: true })
          || await caches.match('./', { ignoreSearch: true });

        if (cachedDoc) return cachedDoc;

        return new Response('<h1>2026 台鐵時刻表 (離線模式)</h1><p>請重新整理載入快取頁面。</p>', {
          headers: { 'Content-Type': 'text/html; charset=utf-8' }
        });
      })()
    );
    return;
  }

  // Strategy B: Static Assets (JSON, PNG, Icons)
  event.respondWith(
    (async () => {
      try {
        const netRes = await fetch(req);
        if (netRes && netRes.ok) {
          const cache = await caches.open(CACHE_NAME);
          cache.put(req, netRes.clone());
          return netRes;
        }
      } catch (e) {
        // Fallback to cache
      }

      const cached = await caches.match(req, { ignoreSearch: true });
      if (cached) return cached;

      return new Response('', { status: 404, statusText: 'Not Found' });
    })()
  );
});
