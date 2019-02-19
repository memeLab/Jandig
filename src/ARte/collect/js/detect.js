/* Change manifest href to use ios-manifest.json on IOS devices */

// Detects if device is on iOS 
const isIos = () => {
    const userAgent = window.navigator.userAgent.toLowerCase();
    return /iphone|ipad|ipod/.test( userAgent );
  }

if (isIos()) {
    document.getElementById("manifest").href = "static/ios-manifest.json";
    // addAppleIcons()
}else {
    document.getElementById("manifest").href = "static/manifest.json";

}

function addAppleIcons() {
    var l = document.createElement('link')
    l.setAttribute('rel', 'apple-touch-icon')
    l.setAttribute('href', '/static/images/icons/AppIconFront.svg')
    document.getElementsByTagName('head')[0].appendChild(l)
}