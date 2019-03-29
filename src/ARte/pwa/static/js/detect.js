/* Change manifest href to use ios-manifest.json on IOS devices */

// Detects if device is on iOS 
const isIos = () => {
    const userAgent = window.navigator.userAgent.toLowerCase();
    return /iphone|ipad|ipod/.test( userAgent );
  }

if (isIos()) {
    document.getElementById("manifest").href = "static/ios-manifest.json";
    const browser = bowser.getParser(window.navigator.userAgent)
    const isValidBrowser = browser.satisfies({
      safari: ">=9"
    })
    if(!isValidBrowser) {
        alert(
          "Desculpe, este aplicativo funciona apenas no navegador Safari :("
        )
    }
}