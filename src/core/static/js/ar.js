async function initializePipeline() {
    await startCamera();
    await opencvReady;

    const DEFAULTS = {
            warpSize: 128,
            borderSize: 26,
            temporalConfirmFrames: 4,
            trackStaleFrames: 60,
            centerTrackThreshold: 60,
            matchConfidenceThreshold: 0.7,
            centroidGrid: 50,
            minArea: 500,
            epsilonCoeff: 0.025,
            blackBorderThreshold: 0.65,
            binaryThreshold: 160,
            useOtsu: true,
            maxSideRatio: 2.0,
            edgeMarginPx: 10
    };
    globalThis.config = { ...DEFAULTS };

    const video = document.getElementById('camera');
    const canvas = document.getElementById('ar-canvas');
    const threeCanvas = document.getElementById('three-canvas');

    const ctx = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    window.arOverlay.initThreeOverlay(threeCanvas, video.videoWidth, video.videoHeight);
    
    let mediaStream = null;
    let animationId = null;
    let started = false;

    globalThis.frameNumber = 0;
    globalThis.video = video;
    globalThis.canvas = canvas;
    globalThis.ctx = ctx;
    globalThis.threeCanvas = threeCanvas;
    globalThis.tracks = new Map();

    globalThis.markerCache = [];

    animationId = requestAnimationFrame(processFrame);
}

function processFrame() {
    globalThis.frameNumber += 1;

    // Draw the current video frame on the processing canvas
    globalThis.ctx.drawImage(globalThis.video, 0, 0, globalThis.canvas.width, globalThis.canvas.height);

    const frame = globalThis.ctx.getImageData(0, 0, globalThis.canvas.width, globalThis.canvas.height);
    const src = cv.matFromImageData(frame);
    const gray = new cv.Mat();
    const dst = new cv.Mat();

    cv.cvtColor(src, gray, cv.COLOR_RGBA2GRAY);
    const thresholdType = globalThis.config.useOtsu ? (cv.THRESH_BINARY | cv.THRESH_OTSU) : cv.THRESH_BINARY;
    cv.threshold(gray, gray, globalThis.config.binaryThreshold, 255, thresholdType);

    const contours = new cv.MatVector();
    const hierarchies = new cv.Mat();
    cv.findContours(gray, contours, hierarchies, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE);
    cv.cvtColor(gray, dst, cv.COLOR_GRAY2RGBA);

    const probableMarkers = {};

    for (let i = 0; i < contours.size(); ++i) {
        const contour = contours.get(i);

        const epsilon = globalThis.config.epsilonCoeff * cv.arcLength(contour, true);
        const approx = new cv.Mat();
        cv.approxPolyDP(contour, approx, epsilon, true);
        contour.delete();
        

        const rect = cv.boundingRect(approx);
        const touchesBorder =
            rect.x <= globalThis.config.edgeMarginPx ||
            rect.y <= globalThis.config.edgeMarginPx ||
            rect.x + rect.width >= globalThis.canvas.width - globalThis.config.edgeMarginPx ||
            rect.y + rect.height >= globalThis.canvas.height - globalThis.config.edgeMarginPx;

        if (approx.rows === 4 && cv.contourArea(approx) > globalThis.config.minArea && cv.isContourConvex(approx) && getSideRatio(approx) <= globalThis.config.maxSideRatio && !touchesBorder) {
            
            const parent = hierarchies.intPtr(0, i)[3];
            if (parent in probableMarkers) {
                // probableMarkers[parent].delete();
                // delete probableMarkers[parent];
            }else{
                probableMarkers[i] = approx;
            }
        } else {
            approx.delete();
        }
    }

    const claimedTrackIds = new Set();
    for (const id in probableMarkers) {
        const approx = probableMarkers[id];

        const warped_marker = warpAndCheckMarker(approx, src);

        if (warped_marker !== null) {
            const center = getApproxCenter(approx);
            let trackId = findNearestTrackId(center, claimedTrackIds);
            if (!trackId) {
                trackId = makeUniqueMarkerId();
            }
            claimedTrackIds.add(trackId);

            updateTrack(trackId, approx, center);
            const marker = tracks.get(trackId);
            if (marker.match == null) {
                const bestMatch = findBestMarkerMatch(warped_marker);
                if (bestMatch) {
                    marker.match = bestMatch;
                    console.log(
                        `Best match for track ${trackId}: ${bestMatch.markerId} rot=${bestMatch.rotationDeg} conf=${bestMatch.confidence.toFixed(3)}`
                    );
                }
                
            } else {
                // Update rotation on tracking
                const rotUpdate = updateRotationForMarker(warped_marker, marker.match.markerId);
                if (rotUpdate) {
                    marker.match.rotationDeg = rotUpdate.rotationDeg;
                    marker.match.confidence = rotUpdate.confidence;
                }
            }
            warped_marker.delete();
        }

        approx.delete();
    }

    pruneStaleTracks();

    let confirmedCount = 0;
    const confirmedIds = [];
    for (const track of tracks.values()) {
        if (track.consecutive >= globalThis.config.temporalConfirmFrames) {
            confirmedCount += 1;
            confirmedIds.push(track.id);
            const confirmedColor = new cv.Scalar(255, 0, 0, 255);
            const contourVec = new cv.MatVector();
            contourVec.push_back(track.approx);
            cv.drawContours(dst, contourVec, -1, confirmedColor, 3, cv.LINE_8);
            contourVec.delete();
        }
    }

    // Update Three.js overlays for confirmed tracks
    if (window.arOverlay) {
        for (const track of globalThis.tracks.values()) {
            if (track.lastSeen === globalThis.frameNumber && track.consecutive >= globalThis.config.temporalConfirmFrames && track.match) {
                window.arOverlay.updateOverlayPose(track.id, track, globalThis.canvas.width, globalThis.canvas.height);
            } else {
                window.arOverlay.hideOverlayMesh(track.id);
            }
        }
        window.arOverlay.cleanupStaleTracks(new Set(tracks.keys()));
        window.arOverlay.renderThreeOverlay();
    }


    frame.data.set(dst.data);
    globalThis.ctx.putImageData(frame, 0, 0);

    src.delete();
    gray.delete();
    dst.delete();
    contours.delete();
    hierarchies.delete();

    animationId = requestAnimationFrame(processFrame);
}

function warpAndCheckMarker(approx, originalSrc) {
    const ordered = orderPoints(approx);
    const srcPts = cv.matFromArray(4, 1, cv.CV_32FC2, [
        ordered[0].x, ordered[0].y,
        ordered[1].x, ordered[1].y,
        ordered[2].x, ordered[2].y,
        ordered[3].x, ordered[3].y,
    ]);
    const dstPts = cv.matFromArray(4, 1, cv.CV_32FC2, [
        0,                 0,
        config.warpSize-1, 0,
        config.warpSize-1, config.warpSize-1,
        0,                 config.warpSize-1,
    ]);

    const M = cv.getPerspectiveTransform(srcPts, dstPts);
    const warped = new cv.Mat();
    cv.warpPerspective(originalSrc, warped, M, new cv.Size(config.warpSize, config.warpSize));

    srcPts.delete();
    dstPts.delete();
    M.delete();

    return warped;
}

function pruneStaleTracks() {
    for (const [key, track] of globalThis.tracks.entries()) {
        if (globalThis.frameNumber - track.lastSeen > globalThis.config.trackStaleFrames) {
            track.approx.delete();
            globalThis.tracks.delete(key);
            if (window.arOverlay) {
                window.arOverlay.removeOverlayMesh(key);
            }
        }
    }
}

function clearmarkerCache() {
    for (const marker of globalThis.markerCache) {
        marker.mat.delete();
    }
    globalThis.markerCache = [];
}

function getExhibitMarkers() {
    if (globalThis.markerCache.length > 0) {
        return globalThis.markerCache;
    }

    clearmarkerCache();

    const imageElements = Array.from(document.querySelectorAll('ar-marker'));
    console.log(`Found ${imageElements.length} ar-marker elements for exhibit markers.`);
    for (const markerEl of imageElements) {
        console.log('Registering marker:', markerEl.markerId, 'src:', markerEl.getAttribute('src'));
        const imgEl = markerEl._markerImg;
        if (!imgEl || !imgEl.complete || imgEl.naturalWidth === 0) continue;

        const markerMat = cv.imread(imgEl, cv.IMREAD_COLOR);
        if (markerMat.empty()) {
            markerMat.delete();
            continue;
        }

        cv.resize(markerMat, markerMat, new cv.Size(config.warpSize, config.warpSize));
        globalThis.markerCache.push({
            id: markerEl.markerId,
            mat: markerMat
        });
    }

    return globalThis.markerCache;
}

function buildRotations(baseMat) {
    const rotations = [
        { degrees: 0, mat: baseMat.clone() }
    ];

    const rotate90 = new cv.Mat();
    cv.rotate(baseMat, rotate90, cv.ROTATE_90_CLOCKWISE);
    rotations.push({ degrees: 90, mat: rotate90 });

    const rotate180 = new cv.Mat();
    cv.rotate(baseMat, rotate180, cv.ROTATE_180);
    rotations.push({ degrees: 180, mat: rotate180 });

    const rotate270 = new cv.Mat();
    cv.rotate(baseMat, rotate270, cv.ROTATE_90_COUNTERCLOCKWISE);
    rotations.push({ degrees: 270, mat: rotate270 });

    return rotations;
}

function findBestMarkerMatch(markerMat) {
    const markers = getExhibitMarkers();
    if (markers.length === 0) {
        return null;
    }

    const rotations = buildRotations(markerMat);
    let bestMatch = null;

    for (const marker of markers) {
        for (const rotation of rotations) {
            const matchResult = new cv.Mat();
            cv.matchTemplate(rotation.mat, marker.mat, matchResult, cv.TM_CCOEFF_NORMED);
            const confidence = matchResult.data32F[0];
            matchResult.delete();

            if (confidence < globalThis.config.matchConfidenceThreshold) {
                continue;
            }

            if (!bestMatch || confidence > bestMatch.confidence) {
                bestMatch = {
                    markerId: marker.id,
                    confidence,
                    rotationDeg: rotation.degrees
                };
            }
        }
    }

    for (const rotation of rotations) {
        rotation.mat.delete();
    }

    return bestMatch;
}

function updateRotationForMarker(markerMat, templateId) {
    const templates = getExhibitMarkers();
    const template = templates.find(t => t.id === templateId);
    if (!template) return null;

    const rotations = buildRotations(markerMat);
    let bestRotation = null;

    for (const rotation of rotations) {
        const matchResult = new cv.Mat();
        cv.matchTemplate(rotation.mat, template.mat, matchResult, cv.TM_CCOEFF_NORMED);
        const confidence = matchResult.data32F[0];
        matchResult.delete();

        if (confidence >= globalThis.config.matchConfidenceThreshold && (!bestRotation || confidence > bestRotation.confidence)) {
            bestRotation = { rotationDeg: rotation.degrees, confidence };
        }
    }

    for (const rotation of rotations) {
        rotation.mat.delete();
    }

    return bestRotation;
}