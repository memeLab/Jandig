importScripts('https://storage.googleapis.com/workbox-cdn/releases/3.6.1/workbox-sw.js');

if (workbox) {
  console.log(`Yay! Workbox is loaded 🎉`);

  workbox.routing.registerRoute(
    new RegExp('.*\.js'),
    workbox.strategies.networkFirst()
  );

  workbox.routing.registerRoute(
    '/',
    workbox.strategies.networkFirst()
  );

  workbox.routing.registerRoute(
    /.*\.(?:png|jpg|jpeg|svg|gif|patt)/,
    workbox.strategies.networkFirst()
  );

  workbox.routing.registerRoute(
    'https://storage.googleapis.com/workbox-cdn/releases/3.6.1/workbox-sw.js',
    workbox.strategies.networkFirst()
  );

} else {
  console.log(`Boo! Workbox didn't load 😬`);
}