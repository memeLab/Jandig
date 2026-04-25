/* Warn iOS users that the AR viewer requires Safari.
 * Only relevant for the AR viewer (WebRTC + WebGL combination that
 * historically only worked on iOS Safari), so this script is loaded
 * exclusively by arviewer.jinja2. Loading it on the CMS would alert
 * iPad/iPhone users on Chrome/Firefox unnecessarily, since the CMS
 * pages render fine on any browser.
 */

(function () {
    const userAgent = window.navigator.userAgent.toLowerCase();
    const isIos = /iphone|ipad|ipod/.test(userAgent);
    if (!isIos) return;

    const browser = bowser.getParser(window.navigator.userAgent);
    const isValidBrowser = browser.satisfies({ safari: ">=9" });
    if (!isValidBrowser) {
        alert(
            "Desculpe, este aplicativo funciona apenas no navegador Safari :("
        );
    }
})();
