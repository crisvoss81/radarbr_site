// static/js/sw.js
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', () => self.clients.claim());
// Pass-through (não cacheia nada por enquanto)
self.addEventListener('fetch', () => {});
