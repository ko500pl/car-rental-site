/* Drive On PWA service worker. Network-first pages, cache-first local assets. */
const CACHE = "drive-on-v3";
/* Pages are cached after their first successful visit. Keeping the large home/map
   documents out of install avoids downloading them twice during first load. */
const CORE = ["/assets/manifest.webmanifest", "/assets/app-icon-192.png", "/assets/app-icon-512.png"];
self.addEventListener("install", event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(CORE)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key))))
    .then(() => self.clients.claim()));
});
self.addEventListener("fetch", event => {
  const request = event.request;
  if (request.method !== "GET" || new URL(request.url).origin !== self.location.origin) return;
  if (request.mode === "navigate") {
    event.respondWith(fetch(request).then(response => {
      const copy = response.clone(); caches.open(CACHE).then(cache => cache.put(request, copy)); return response;
    }).catch(() => caches.match(request).then(hit => hit || caches.match("/"))));
    return;
  }
  event.respondWith(caches.match(request).then(hit => hit || fetch(request).then(response => {
    if (response.ok) { const copy = response.clone(); caches.open(CACHE).then(cache => cache.put(request, copy)); }
    return response;
  })));
});
