let mediaStream;

async function startCamera() {
    const userCamera = document.getElementById('camera');
    try {
        mediaStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment", height: {min: 480, ideal: 720,max: 1080 }}, audio: false });
        userCamera.srcObject = mediaStream;
        await userCamera.play();
        await waitForVideoMetadata(userCamera);
    } catch (error) {
        console.error('Camera access failed. Please allow webcam permissions.');
        throw error;
    }
}

function waitForVideoMetadata(video) {
    if (video.readyState >= 1 && video.videoWidth > 0 && video.videoHeight > 0) {
        return Promise.resolve();
    }

    return new Promise((resolve) => {
        video.addEventListener('loadedmetadata', () => resolve(), { once: true });
    });
}

// CSS `object-fit: cover` shows only the center portion of the camera frame that matches
// the screen's aspect ratio. Return that visible rectangle (in source video pixels) so the
// pipeline can process just what the user actually sees.
function computeVisibleCrop(videoW, videoH, viewW, viewH) {
    const viewAspect = viewW / viewH;
    const videoAspect = videoW / videoH;

    let cropW;
    let cropH;
    if (videoAspect > viewAspect) {
        // Camera is wider than the screen -> crop the left/right edges.
        cropH = videoH;
        cropW = Math.round(videoH * viewAspect);
    } else {
        // Camera is taller than the screen -> crop the top/bottom edges.
        cropW = videoW;
        cropH = Math.round(videoW / viewAspect);
    }

    const cropX = Math.round((videoW - cropW) / 2);
    const cropY = Math.round((videoH - cropH) / 2);
    return { x: cropX, y: cropY, width: cropW, height: cropH };
}

let _opencvResolve;
const opencvReady = new Promise((resolve) => { _opencvResolve = resolve; });
function MarkOpenCvReady() {
    if (!globalThis.cv) {
        console.error('OpenCV failed to load.');
        return;
    }
    // The script `onload` fires when the JS is parsed, but the WASM runtime may not
    // be initialized yet (cv.Mat and friends are undefined until then). Wait for the
    // runtime before resolving so callers can safely construct cv.Mat / call cv.imread.
    if (typeof cv.then === 'function') {
        // Modularized build: `cv` is a promise resolving to the ready module.
        cv.then((readyCv) => {
            globalThis.cv = readyCv;
            _opencvResolve();
        });
    } else if (typeof cv.Mat === 'function') {
        // Runtime already initialized.
        _opencvResolve();
    } else {
        // Classic build: resolve once the WASM runtime finishes initializing.
        cv['onRuntimeInitialized'] = () => _opencvResolve();
    }
}

function getSideRatio(approx) {
    const sides = [];
    for (let i = 0; i < 4; i++) {
        const x1 = approx.data32S[i * 2];
        const y1 = approx.data32S[i * 2 + 1];
        const x2 = approx.data32S[((i + 1) % 4) * 2];
        const y2 = approx.data32S[((i + 1) % 4) * 2 + 1];
        const dx = x2 - x1;
        const dy = y2 - y1;
        sides.push(Math.hypot(dx, dy));
    }
    const minSide = Math.min(...sides);
    const maxSide = Math.max(...sides);
    return minSide > 0 ? (maxSide / minSide) : Infinity;
}

function orderPoints(approx) {
    const pts = [];
    for (let i = 0; i < 4; i++) {
        pts.push({ x: approx.data32S[i * 2], y: approx.data32S[i * 2 + 1] });
    }

    pts.sort((a, b) => (a.x + a.y) - (b.x + b.y));
    const tl = pts[0];
    const br = pts[3];
    const mid = [pts[1], pts[2]];
    mid.sort((a, b) => (a.y - a.x) - (b.y - b.x));
    return [tl, mid[0], br, mid[1]];
}

function getApproxCenter(approx) {
    let cx = 0;
    let cy = 0;
    for (let i = 0; i < 4; i++) {
        cx += approx.data32S[i * 2];
        cy += approx.data32S[i * 2 + 1];
    }
    return { x: cx / 4, y: cy / 4 };
}

function findNearestTrackId(center, claimedTrackIds) {
    let bestTrackId = null;
    let bestDistance = Infinity;

    for (const [trackId, track] of globalThis.tracks.entries()) {
        if (claimedTrackIds.has(trackId)) {
            continue;
        }
        const distance = centerDistance(center, track.center);
        if (distance <= config.centerTrackThreshold && distance < bestDistance) {
            bestDistance = distance;
            bestTrackId = trackId;
        }
    }

    return bestTrackId;
}

function centerDistance(a, b) {
    return Math.hypot(a.x - b.x, a.y - b.y);
}

function makeMarkerId() {
    let id = '';
    while (id.length < 8) {
        id += Math.random().toString(16).slice(2);
    }
    return id.slice(0, 8);
}

function makeUniqueMarkerId() {
    let markerId = makeMarkerId();
    while (globalThis.tracks.has(markerId)) {
        markerId = makeMarkerId();
    }
    return markerId;
}

function updateTrack(trackId, approx, center) {
    const prev = globalThis.tracks.get(trackId);
    if (!prev) {
        globalThis.tracks.set(trackId, {
            id: trackId,
            consecutive: 1,
            lastSeen: frameNumber,
            approx: approx.clone(),
            center,
            match: null
        });
        return;
    }

    prev.consecutive = prev.lastSeen === frameNumber - 1 ? prev.consecutive + 1 : 1;
    prev.lastSeen = frameNumber;
    prev.approx.delete();
    prev.approx = approx.clone();
    prev.center = center;
}