/* Change manifest href to use ios-manifest.json on iOS devices.
 * Safe to load on every page; the AR-only browser-compatibility
 * warning lives in safari-only-warning.js and is loaded only by
 * arviewer.jinja2.
 */

// Detects if device is on iOS
const isIos = () => {
    const userAgent = window.navigator.userAgent.toLowerCase();
    return /iphone|ipad|ipod/.test( userAgent );
  }

if (isIos()) {
    document.getElementById("manifest").href = "/static/ios-manifest.json";
}