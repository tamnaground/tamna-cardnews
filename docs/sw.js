/* 성읍민속마을 안내 — 오프라인 지원 (네트워크 우선, 캐시 폴백) */
var CACHE = 'seongeup-guide-v1';
var SHELL = ['index.html', 'style.css', 'app.js', 'data/spots.js', 'manifest.webmanifest'];

self.addEventListener('install', function (e) {
  e.waitUntil(
    caches.open(CACHE).then(function (c) { return c.addAll(SHELL); }).then(function () {
      return self.skipWaiting();
    })
  );
});

self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); }));
    }).then(function () { return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function (e) {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    fetch(e.request)
      .then(function (res) {
        if (res.ok && new URL(e.request.url).origin === location.origin) {
          var copy = res.clone();
          caches.open(CACHE).then(function (c) { c.put(e.request, copy); });
        }
        return res;
      })
      .catch(function () {
        return caches.match(e.request, { ignoreSearch: e.request.mode === 'navigate' }).then(function (hit) {
          if (hit) return hit;
          if (e.request.mode === 'navigate') return caches.match('index.html');
          return Response.error();
        });
      })
  );
});
