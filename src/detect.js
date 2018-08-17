/* Change manifest href to use ios-manifest.json on IOS devices */

// Detects if device is on iOS 
const isIos = () => {
    const userAgent = window.navigator.userAgent.toLowerCase();
    return /iphone|ipad|ipod/.test( userAgent );
  }

if (isIos()) {
    document.getElementById("manifest").href = "ios-manifest.json";
}