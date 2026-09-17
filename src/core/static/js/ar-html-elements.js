let markerCounter = 0;

// Resolve once the given <img> has finished (or failed) loading, logging download time.
function imageReady(img, id, loadStart) {
    return new Promise((resolve) => {
        if (img.complete && img.naturalWidth > 0) {
            console.log(`[AR] ${id} asset downloaded in ${Math.round(performance.now() - loadStart)}ms`);
            resolve();
            return;
        }
        img.addEventListener('load', () => {
            console.log(`[AR] ${id} asset downloaded in ${Math.round(performance.now() - loadStart)}ms`);
            resolve();
        }, { once: true });
        img.addEventListener('error', () => {
            console.warn(`[AR] ${id} asset failed to load`);
            resolve();
        }, { once: true });
    });
}

class ARMarkerElement extends HTMLElement {
    connectedCallback() {
        this.style.display = 'none';
        this.markerId = 'marker-' + (markerCounter++);

        // Load the marker image for OpenCV detection
        const src = this.getAttribute('src');
        if (src) {
            const loadStart = performance.now();
            this._markerImg = new Image();
            this._markerImg.crossOrigin = 'anonymous';
            // `ready` lets the pipeline await this asset before building caches.
            this.ready = imageReady(this._markerImg, this.markerId, loadStart);
            this._markerImg.src = src;
        } else {
            this.ready = Promise.resolve();
        }
    }
}

class ARContentElement extends HTMLElement {
    connectedCallback() {
        this.style.display = 'none';
        this.type = this.getAttribute('type');
        this.metadata_url = this.getAttribute('metadata') || null;
        this.src = this.getAttribute('src');

        const contentId = this.id || 'content';
        const loadStart = performance.now();

        if (this.type === 'video') {
            this.video = document.createElement('video');
            this.video.crossOrigin = 'anonymous';
            this.video.loop = true;
            this.video.muted = true;
            this.video.playsInline = true;
            this.video.preload = 'auto';
            this.ready = new Promise((resolve) => {
                this.video.addEventListener('loadeddata', () => {
                    console.log(`[AR] ${contentId} asset downloaded in ${Math.round(performance.now() - loadStart)}ms`);
                    resolve();
                }, { once: true });
                this.video.addEventListener('error', () => {
                    console.warn(`[AR] ${contentId} video failed to load`);
                    resolve();
                }, { once: true });
            });
            this.video.src = this.getAttribute('src');
        } else if (this.type === 'spritesheet') {
            this.spritesheet = document.createElement('img');
            this.spritesheet.crossOrigin = 'anonymous';
            const imgPromise = imageReady(this.spritesheet, contentId, loadStart);
            this.spritesheet.src = this.getAttribute('src');

            let metaPromise;
            if (this.metadata_url) {
                metaPromise = fetch(this.metadata_url)
                    .then(r => r.json())
                    .then(meta => { this.metadata = meta; })
                    .catch(e => console.warn('Failed to load spritesheet metadata:', e));
            } else {
                console.warn('Spritesheet metadata not provided for', this);
                metaPromise = Promise.resolve();
            }
            this.ready = Promise.all([imgPromise, metaPromise]);
        } else {
            this.image = document.createElement('img');
            this.image.crossOrigin = 'anonymous';
            this.ready = imageReady(this.image, contentId, loadStart);
            this.image.src = this.getAttribute('src');
        }
    }
}

customElements.define('ar-marker', ARMarkerElement);
customElements.define('ar-content', ARContentElement);

// Await every marker + content asset in the exhibit, reporting fractional progress.
// A timeout guard prevents a single broken/slow asset from stalling startup.
function waitForExhibitAssets(onProgress, timeoutMs = 60000) {
    const elements = [
        ...document.querySelectorAll('ar-marker'),
        ...document.querySelectorAll('ar-content'),
    ];
    const total = elements.length;

    if (total === 0) {
        if (onProgress) onProgress(1);
        return Promise.resolve();
    }

    let completed = 0;
    const track = (p) => Promise.resolve(p).then(() => {
        completed += 1;
        if (onProgress) onProgress(completed / total);
    });

    const all = Promise.all(elements.map((el) => track(el.ready)));

    return new Promise((resolve) => {
        let settled = false;
        const timer = setTimeout(() => {
            if (settled) return;
            settled = true;
            console.warn(`[AR] waitForExhibitAssets timed out after ${timeoutMs}ms (${completed}/${total} ready)`);
            resolve();
        }, timeoutMs);

        all.then(() => {
            if (settled) return;
            settled = true;
            clearTimeout(timer);
            resolve();
        });
    });
}
