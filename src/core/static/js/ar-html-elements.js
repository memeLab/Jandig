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
    }
}

class ARContentElement extends HTMLElement {
    connectedCallback() {
        this.style.display = 'none';
        this.type = this.getAttribute('type');
        this.metadata = this.getAttribute('metadata') || null;
        this.src = this.getAttribute('src');

        if (this.type === 'video') {
            this.video = document.createElement('video');
            this.video.crossOrigin = 'anonymous';
            this.video.src = this.getAttribute('src');
            this.video.loop = true;
            this.video.muted = true;
            this.video.playsInline = true;
            this.video.preload = 'auto';
        } else if (this.type === 'spritesheet') {
            this.spritesheet = document.createElement('img');
            this.spritesheet.crossOrigin = 'anonymous';
            this.spritesheet.src = this.getAttribute('src');
            if (this.metadata) {
                fetch(this.metadata)
                    .then(r => r.json())
                    .then(meta => { this.spritesheetMetadata = meta; })
                    .catch(e => console.warn('Failed to load spritesheet metadata:', e));
            } else{
                console.warn('Spritesheet metadata not provided for', this);
            }

        } else {
            this.image = document.createElement('img');
            this.image.crossOrigin = 'anonymous';
            this.image.src = this.getAttribute('src');
        }
    }
}

customElements.define('ar-marker', ARMarkerElement);
customElements.define('ar-content', ARContentElement);
