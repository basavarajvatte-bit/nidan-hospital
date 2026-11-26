// Offline shell cache. Patient data is never cached here.
const CACHE = "nidan-v32";
const SHELL = ["./", "index.html", "style.css", "app.js", "config.js", "manifest.json", "icon.svg", "reception.js", "dashboard.js", "nursing.js", "nidan.js", "agents.js", "chat.js", "timeline.js", "search.js", "appointments.js", "accounts.js", "pharmacy.js", "lab.js", "hr.js", "ops.js", "records.js", "quality.js", "boss.js"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))));
  self.clients.claim();
});

// Network first (so updates show), cache only as offline fallback. Same-origin GET only.
self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.origin !== location.origin) return;
  e.respondWith(
    fetch(e.request, { cache: "no-cache" })
      .then(res => { const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); return res; })
      .catch(() => caches.match(e.request, { ignoreSearch: true }))
  );
});
