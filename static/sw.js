/**
 * SkillRock Progressive Web App (PWA) Service Worker
 * Provides offline caching, lightning-fast static asset delivery, and installability.
 */

const CACHE_NAME = "skillrock-v1.2.0";

const PRECACHE_ASSETS = [
  "/",
  "/static/css/style.css",
  "/static/css/mobile.css",
  "/static/img/logo.jpg",
  "/static/img/icon-192.png",
  "/static/img/icon-512.png",
  "/static/img/apple-touch-icon.png",
  "/static/manifest.json"
];

// 1. Install Event — Pre-cache core app shell
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(PRECACHE_ASSETS).catch((err) => {
        console.warn("[SkillRock SW] Pre-cache partial warning:", err);
      });
    }).then(() => self.skipWaiting())
  );
});

// 2. Activate Event — Clean up outdated caches
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// 3. Fetch Event — Stale-While-Revalidate for static assets, Network-First for HTML
self.addEventListener("fetch", (event) => {
  const request = event.request;
  const url = new URL(request.url);

  // Skip non-GET requests, chrome extensions, analytics, or external origins
  if (request.method !== "GET" || !url.protocol.startsWith("http")) {
    return;
  }

  // Never cache sensitive authenticated API endpoints or admin routes
  if (
    url.pathname.startsWith("/admin") ||
    url.pathname.startsWith("/auth") ||
    url.pathname.startsWith("/signin") ||
    url.pathname.startsWith("/logout") ||
    url.pathname.startsWith("/api") ||
    url.pathname.startsWith("/healthz")
  ) {
    return;
  }

  // A. Static Assets (CSS, JS, Images, Fonts) — Cache-First with Background Revalidation
  if (url.pathname.startsWith("/static/") || url.pathname.endsWith(".css") || url.pathname.endsWith(".js") || url.pathname.endsWith(".png") || url.pathname.endsWith(".jpg")) {
    event.respondWith(
      caches.match(request).then((cachedResponse) => {
        const fetchPromise = fetch(request).then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const responseClone = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, responseClone);
            });
          }
          return networkResponse;
        }).catch(() => cachedResponse);

        return cachedResponse || fetchPromise;
      })
    );
    return;
  }

  // B. HTML Pages / Navigations — Network-First with Cache Fallback for instant speed
  if (request.mode === "navigate" || request.headers.get("accept")?.includes("text/html")) {
    event.respondWith(
      fetch(request)
        .then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const responseClone = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, responseClone);
            });
          }
          return networkResponse;
        })
        .catch(() => {
          return caches.match(request).then((cachedResponse) => {
            if (cachedResponse) {
              return cachedResponse;
            }
            return caches.match("/");
          });
        })
    );
    return;
  }
});
