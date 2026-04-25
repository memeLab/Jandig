importScripts('https://storage.googleapis.com/workbox-cdn/releases/3.6.1/workbox-sw.js');

// Activate the new SW immediately so existing users stop being served
// HTML from the old "cache everything" version (see #506).
self.addEventListener('install', (event) => self.skipWaiting());
self.addEventListener('activate', (event) => self.clients.claim());

if (workbox) {
  console.log(`Yay! Workbox is loaded 🎉`);

  // Cache only static assets — never HTML responses. Caching HTML
  // produced cross-user state leaks and stale CSRF tokens (#506):
  // when User B visited a page after User A had loaded it on the
  // same browser, the SW could serve A's cached page (with A's
  // username and CSRF token), and a subsequent setlang POST then
  // failed with 403 because the CSRF token was bound to A's session.
  //
  // Static assets are origin-wide and don't carry per-user state,
  // so they're safe to cache; let HTML always go to the network.

  workbox.routing.registerRoute(
    /.*\.(?:png|jpg|jpeg|svg|gif|patt|webp|ico)$/,
    workbox.strategies.networkFirst()
  );

  workbox.routing.registerRoute(
    /.*\.(?:js|css)$/,
    workbox.strategies.networkFirst()
  );

  workbox.routing.registerRoute(
    /.*\.(?:woff|woff2|ttf|eot|otf)$/,
    workbox.strategies.cacheFirst()
  );

  workbox.routing.registerRoute(
    'https://storage.googleapis.com/workbox-cdn/releases/3.6.1/workbox-sw.js',
    workbox.strategies.networkFirst()
  );

} else {
  console.log(`Boo! Workbox didn't load 😬`);
}