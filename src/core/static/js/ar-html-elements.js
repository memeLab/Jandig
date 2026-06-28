let markerCounter = 0;

class ARMarkerElement extends HTMLElement {
    connectedCallback() {
        this.style.display = 'none';
        this.markerId = 'marker-' + (markerCounter++);

        // Load the marker image for OpenCV detection
        const src = this.getAttribute('src');
        if (src) {
            this._markerImg = new Image();
            this._markerImg.crossOrigin = 'anonymous';
            this._markerImg.src = src;
        }

        // Find the ar-content child for the overlay
        const contentEl = this.querySelector('ar-content');
        if (contentEl) {
            const contentSrc = contentEl.getAttribute('src');
            const contentType = contentEl.getAttribute('type') || 'img';
            const metadataUrl = contentEl.getAttribute('metadata');

            this._contentType = contentType;
            this._contentMetadata = null;

            if (contentType === 'video' && contentSrc) {
                this._contentVideo = document.createElement('video');
                this._contentVideo.crossOrigin = 'anonymous';
                this._contentVideo.src = contentSrc;
                this._contentVideo.loop = true;
                this._contentVideo.muted = true;
                this._contentVideo.playsInline = true;
                this._contentVideo.preload = 'auto';
            } else if (contentSrc) {
                this._contentImg = new Image();
                this._contentImg.crossOrigin = 'anonymous';
                this._contentImg.src = contentSrc;
            }

            if (contentType === 'spritesheet' && metadataUrl) {
                fetch(metadataUrl)
                    .then(r => r.json())
                    .then(meta => { this._contentMetadata = meta; })
                    .catch(e => console.warn('Failed to load spritesheet metadata:', e));
            }
        }
    }
}

class ARContentElement extends HTMLElement {
    connectedCallback() {
        this.style.display = 'none';
    }
}

customElements.define('ar-marker', ARMarkerElement);
customElements.define('ar-content', ARContentElement);
