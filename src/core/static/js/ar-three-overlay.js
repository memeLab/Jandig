import * as THREE from 'three';

let renderer, scene, camera;
let canvasWidth = 0, canvasHeight = 0;
let focalLength = 0;

const overlayMeshes = new Map(); // trackId -> THREE.Mesh
const textureCache = new Map(); // markerId -> THREE.Texture
const spritesheetState = new Map(); // trackId -> { meta, lastFrameTime, currentFrame }
const videoState = new Map(); // trackId -> { markerId, video, playing }

export function initThreeOverlay(threeCanvas, width, height) {
    canvasWidth = width;
    canvasHeight = height;
    focalLength = width; // approximate: fx ≈ fy ≈ canvas width

    renderer = new THREE.WebGLRenderer({ canvas: threeCanvas, alpha: true, antialias: true });
    renderer.setSize(width, height, false); // false = don't set CSS style, let CSS handle display size
    renderer.setClearColor(0x000000, 0);

    scene = new THREE.Scene();

    // Perspective camera with projection matrix matching approximate webcam intrinsics
    // We'll set the projection matrix manually from intrinsics
    camera = new THREE.PerspectiveCamera();
    camera.matrixAutoUpdate = false;
    setCameraProjection(width, height, focalLength);

    scene.add(camera);
}

function setCameraProjection(w, h, f) {
    // Build an OpenGL-style projection matrix from camera intrinsics
    // Intrinsics: fx=f, fy=f, cx=w/2, cy=h/2
    // Near/far clipping planes
    const near = 0.1;
    const far = 1000;
    const cx = w / 2;
    const cy = h / 2;

    // OpenGL NDC projection from pinhole camera intrinsics
    // Maps camera-space (x-right, y-down, z-forward) to clip space
    const projMatrix = new THREE.Matrix4();
    projMatrix.set(
        2 * f / w,  0,          0,                          0,
        0,          2 * f / h,  0,                          0,
        0,          0,          -(far + near) / (far - near), -2 * far * near / (far - near),
        0,          0,          -1,                         0
    );
    camera.projectionMatrix.copy(projMatrix);
    camera.projectionMatrixInverse.copy(projMatrix).invert();
}

function getMarkerElement(markerId) {
    const markerEl = document.getElementById(markerId);
    return markerEl || null;
}
function getContentElement(markerId) {
    const id = markerId.replace('marker-', 'content-');
    const contentEl = document.getElementById(id);
    return contentEl || null;
}

function getOrCreateTexture(markerId) {
    if (textureCache.has(markerId)) {
        return textureCache.get(markerId);
    }

    const contentEl = getContentElement(markerId);
    if (!contentEl) return null;


    let texture;

    if (contentEl.type === 'video' && contentEl.video) {
        texture = new THREE.VideoTexture(contentEl.video);
        texture.minFilter = THREE.LinearFilter;
        texture.magFilter = THREE.LinearFilter;
        texture.colorSpace = THREE.SRGBColorSpace;
    } else {
        const imgEl = contentEl.image || contentEl.spritesheet;
        if (!imgEl) {
            console.warn('No image or spritesheet found for content element', contentEl);
            return null;
        }

        texture = new THREE.Texture(imgEl);
        texture.needsUpdate = true;
        texture.minFilter = THREE.LinearFilter;
        texture.magFilter = THREE.LinearFilter;
        texture.colorSpace = THREE.SRGBColorSpace;

        // For spritesheets, set up UV repeat to show a single frame
        if (contentEl.type === 'spritesheet' && contentEl.metadata) {
            const meta = contentEl.metadata;
            texture.repeat.set(1 / meta.columns, 1 / meta.rows);
            texture.offset.set(0, 1 - (1 / meta.rows)); // start at top-left frame
        }
    }

    textureCache.set(markerId, texture);
    return texture;
}

function getOrCreateMesh(trackId, markerId) {
    if (overlayMeshes.has(trackId)) {
        return overlayMeshes.get(trackId);
    }

    const contentEl = getContentElement(markerId);
    if (!contentEl) return null;

    const texture = getOrCreateTexture(markerId);
    if (!texture) return null;

    // Set up spritesheet animation state if needed
    if (contentEl.type === 'spritesheet' && contentEl.metadata) {
        spritesheetState.set(trackId, {
            markerId: markerId,
            meta: contentEl.metadata,
            lastFrameTime: performance.now(),
            currentFrame: 0,
        });
    }

    // Set up video state if needed
    if (contentEl.type === 'video' && contentEl.video) {
        videoState.set(trackId, {
            markerId: markerId,
            video: contentEl.video,
            playing: false,
        });
    }

    const geometry = new THREE.PlaneGeometry(1, 1);
    // Flip UVs horizontally to correct mirror caused by coordinate system conversion
    const uvAttr = geometry.attributes.uv;
    for (let i = 0; i < uvAttr.count; i++) {
        uvAttr.setX(i, 1.0 - uvAttr.getX(i));
    }
    uvAttr.needsUpdate = true;

    const material = new THREE.MeshBasicMaterial({
        map: texture,
        side: THREE.DoubleSide,
        transparent: true,
    });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.matrixAutoUpdate = false;

    scene.add(mesh);
    overlayMeshes.set(trackId, mesh);
    return mesh;
}

export function removeOverlayMesh(trackId) {
    const mesh = overlayMeshes.get(trackId);
    if (mesh) {
        scene.remove(mesh);
        mesh.geometry.dispose();
        mesh.material.dispose();
        overlayMeshes.delete(trackId);
    }
    spritesheetState.delete(trackId);
    const vs = videoState.get(trackId);
    if (vs) {
        vs.video.pause();
        videoState.delete(trackId);
    }
}

export function hideOverlayMesh(trackId) {
    const mesh = overlayMeshes.get(trackId);
    if (mesh) mesh.visible = false;
    // Pause video when hidden
    const vs = videoState.get(trackId);
    if (vs && vs.playing) {
        vs.video.pause();
        vs.playing = false;
    }
}

/**
 * Estimate the 3D pose of a marker from its 4 detected corners using cv.solvePnP,
 * then update the corresponding Three.js mesh's matrix.
 *
 * @param {string} trackId - The track identifier
 * @param {object} track - The track object with .approx (cv.Mat of 4 corners), .match
 * @param {number} w - Canvas width
 * @param {number} h - Canvas height
 */
export function updateOverlayPose(trackId, track, w, h) {
    if (!track.match) return;

    const mesh = getOrCreateMesh(trackId, track.match.markerId);
    if (!mesh) return;

    mesh.visible = true;

    // Start video playback if this is a video content track
    const vs = videoState.get(trackId);
    if (vs && !vs.playing) {
        vs.video.play().catch(() => {});
        vs.playing = true;
    }

    // Get ordered image points from the detected contour
    const ordered = orderPointsFromApprox(track.approx);

    // 3D object points: a unit square centered at origin on the XY plane
    // Points ordered: TL, TR, BR, BL
    const objectPoints = cv.matFromArray(4, 1, cv.CV_64FC3, [
        -0.5, -0.5, 0,
         0.5, -0.5, 0,
         0.5,  0.5, 0,
        -0.5,  0.5, 0,
    ]);

    // 2D image points from detection
    const imagePoints = cv.matFromArray(4, 1, cv.CV_64FC2, [
        ordered[0].x, ordered[0].y,
        ordered[1].x, ordered[1].y,
        ordered[2].x, ordered[2].y,
        ordered[3].x, ordered[3].y,
    ]);

    // Camera intrinsic matrix
    const f = focalLength;
    const cx = w / 2;
    const cy = h / 2;
    const cameraMatrix = cv.matFromArray(3, 3, cv.CV_64FC1, [
        f,  0,  cx,
        0,  f,  cy,
        0,  0,  1,
    ]);

    const distCoeffs = cv.Mat.zeros(4, 1, cv.CV_64FC1);
    const rvec = new cv.Mat();
    const tvec = new cv.Mat();

    try {
        const success = cv.solvePnP(objectPoints, imagePoints, cameraMatrix, distCoeffs, rvec, tvec);
        if (!success) {
            mesh.visible = false;
            return;
        }

        // Convert rotation vector to rotation matrix
        const rotMat = new cv.Mat();
        cv.Rodrigues(rvec, rotMat);

        // Build 4x4 model-view matrix from [R|t]
        // OpenCV: x-right, y-down, z-forward
        // Three.js: x-right, y-up, z-out-of-screen
        // We need to flip Y and Z axes
        const r = rotMat.data64F;
        const t = tvec.data64F;

        // Apply axis conversion: multiply by diag(1, -1, -1) on the left
        // This flips Y and Z to go from OpenCV to OpenGL/Three.js convention
        const modelViewMatrix = new THREE.Matrix4();
        modelViewMatrix.set(
            r[0],  r[1],  r[2],  t[0],
            -r[3], -r[4], -r[5], -t[1],
            -r[6], -r[7], -r[8], -t[2],
            0,     0,     0,     1
        );

        // Apply local Z rotation: 180° base correction (coordinate system flip causes
        // the texture to appear upside down) plus the detected template rotation
        const rotDeg = (track.match.rotationDeg || 0) + 180;
        const localRotation = new THREE.Matrix4();
        localRotation.makeRotationZ(-rotDeg * Math.PI / 180);
        modelViewMatrix.multiply(localRotation);

        // Small Z offset so the overlay floats slightly above the marker surface
        const zOffset = new THREE.Matrix4();
        zOffset.makeTranslation(0, 0, 0.01);
        modelViewMatrix.multiply(zOffset);

        mesh.matrix.copy(modelViewMatrix);
        mesh.matrixWorldNeedsUpdate = true;

        rotMat.delete();
    } catch (e) {
        console.warn('solvePnP failed for track', trackId, e);
        mesh.visible = false;
    } finally {
        objectPoints.delete();
        imagePoints.delete();
        cameraMatrix.delete();
        distCoeffs.delete();
        rvec.delete();
        tvec.delete();
    }
}

function orderPointsFromApprox(approx) {
    const pts = [];
    for (let i = 0; i < 4; i++) {
        pts.push({ x: approx.data32S[i * 2], y: approx.data32S[i * 2 + 1] });
    }

    // Sort by angle from centroid — this gives a perfectly stable cyclic
    // ordering regardless of rotation (unlike the x+y heuristic which flips at 45°)
    const cx = (pts[0].x + pts[1].x + pts[2].x + pts[3].x) / 4;
    const cy = (pts[0].y + pts[1].y + pts[2].y + pts[3].y) / 4;

    pts.sort((a, b) => {
        return Math.atan2(a.y - cy, a.x - cx) - Math.atan2(b.y - cy, b.x - cx);
    });

    // pts is now in consistent counter-clockwise order (screen coords, so visually CW)
    // Find the corner closest to top-left (smallest x + y) as the starting anchor
    let minSum = Infinity;
    let startIdx = 0;
    for (let i = 0; i < 4; i++) {
        const sum = pts[i].x + pts[i].y;
        if (sum < minSum) {
            minSum = sum;
            startIdx = i;
        }
    }

    // Return in order: TL, TR, BR, BL (cyclic from startIdx)
    return [
        pts[startIdx],
        pts[(startIdx + 1) % 4],
        pts[(startIdx + 2) % 4],
        pts[(startIdx + 3) % 4],
    ];
}

export function renderThreeOverlay() {
    if (!renderer) return;

    // Advance spritesheet animations
    const now = performance.now();
    for (const [trackId, state] of spritesheetState) {
        const { meta, lastFrameTime, currentFrame, markerId } = state;
        const elapsed = now - lastFrameTime;
        if (elapsed >= meta.frameDurationMs) {
            const framesToAdvance = Math.floor(elapsed / meta.frameDurationMs);
            const nextFrame = (currentFrame + framesToAdvance) % meta.frames;
            state.currentFrame = nextFrame;
            state.lastFrameTime = now - (elapsed % meta.frameDurationMs);

            // Update texture UV offset for the new frame
            const texture = textureCache.get(markerId);
            if (texture) {
                const col = nextFrame % meta.columns;
                const row = Math.floor(nextFrame / meta.columns);
                texture.offset.set(col / meta.columns, 1 - (row + 1) / meta.rows);
            }
        }
    }

    renderer.render(scene, camera);
}

export function resizeThreeOverlay(width, height) {
    if (!renderer) return;
    canvasWidth = width;
    canvasHeight = height;
    focalLength = width;
    renderer.setSize(width, height, false);
    setCameraProjection(width, height, focalLength);
}

export function cleanupStaleTracks(activeTrackIds) {
    for (const [trackId] of overlayMeshes) {
        if (!activeTrackIds.has(trackId)) {
            removeOverlayMesh(trackId);
        }
    }
}
