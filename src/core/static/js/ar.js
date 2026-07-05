async function initializePipeline() {
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
            edgeMarginPx: 10,
            rotationMatchSize: 48
    };
    globalThis.config = { ...DEFAULTS };
    globalThis.frameNumber = 0;
    globalThis.tracks = new Map();
    globalThis.markerCache = [];

    // Weighted phases drive a single monotonic 0-100% loading bar.
    const WEIGHTS = { assets: 0.5, opencv: 0.25, three: 0.25 };
    let progressBase = 0;
    const phaseProgress = (weight, label) => (fraction) => {
        setLoadingProgress((progressBase + weight * fraction) * 100, label);
    };

    setLoadingProgress(0, 'Preparing exhibit…');

    // OpenCV runtime must be ready before we can build the marker cache.
    await opencvReady;

    // Phase 1: download every marker + content asset for this exhibit.
    await waitForExhibitAssets(phaseProgress(WEIGHTS.assets, 'Downloading assets…'));
    progressBase += WEIGHTS.assets;

    // Phase 2: build the OpenCV template cache (image + 4 rotations per marker).
    buildMarkerCache(phaseProgress(WEIGHTS.opencv, 'Building marker cache…'));
    progressBase += WEIGHTS.opencv;

    // Camera + rendering surfaces (camera starts only after assets are cached).
    await startCamera();

    const video = document.getElementById('camera');
    const canvas = document.getElementById('ar-canvas');
    const threeCanvas = document.getElementById('three-canvas');

    const ctx = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    globalThis.arOverlay.initThreeOverlay(threeCanvas, video.videoWidth, video.videoHeight);

    // Phase 3: prewarm Three.js textures and force GPU uploads.
    globalThis.arOverlay.prewarmOverlayCache(phaseProgress(WEIGHTS.three, 'Caching animations…'));
    progressBase += WEIGHTS.three;

    setLoadingProgress(100, 'Ready');
    hideLoading();

    globalThis.video = video;
    globalThis.canvas = canvas;
    globalThis.ctx = ctx;
    globalThis.threeCanvas = threeCanvas;

    requestAnimationFrame(processFrame);
}

function setLoadingProgress(pct, label) {
    const bar = document.getElementById('ar-loading-bar');
    const text = document.getElementById('ar-loading-label');
    const clamped = Math.max(0, Math.min(100, Math.round(pct)));
    if (bar) bar.style.width = clamped + '%';
    if (text && label) text.textContent = label;
}

function hideLoading() {
    const overlay = document.getElementById('ar-loading');
    if (overlay) overlay.hidden = true;
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
                    // Give each track a distinct phase so periodic rotation updates are
                    // spread across frames instead of all firing on the same frame
                    // (a synchronized burst caused a periodic stutter on mobile).
                    globalThis.rotationPhaseCounter = (globalThis.rotationPhaseCounter || 0) + 1;
                    marker.rotationPhase = globalThis.rotationPhaseCounter;
                    console.log(
                        `Best match for track ${trackId}: ${bestMatch.markerId} rot=${bestMatch.rotationDeg} conf=${bestMatch.confidence.toFixed(3)}`
                    );
                }
                
            } else {
                // Update marker best rotation on tracking periodically to reduce computation.
                // Offset by the track's phase so only a subset of markers recompute per frame.
                if ((globalThis.frameNumber + (marker.rotationPhase || 0)) % 20 === 0) {
                    const rotUpdate = updateRotationForMarker(warped_marker, marker.match.markerId);
                    if (rotUpdate) {
                        marker.match.rotationDeg = rotUpdate.rotationDeg;
                        marker.match.confidence = rotUpdate.confidence;
                    }
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
    if (globalThis.arOverlay) {
        for (const track of globalThis.tracks.values()) {
            if (track.lastSeen === globalThis.frameNumber && track.consecutive >= globalThis.config.temporalConfirmFrames && track.match) {
                globalThis.arOverlay.updateOverlayPose(track.id, track, globalThis.canvas.width, globalThis.canvas.height);
            } else {
                globalThis.arOverlay.hideOverlayMesh(track.id);
            }
        }
        globalThis.arOverlay.cleanupStaleTracks(new Set(tracks.keys()));
        globalThis.arOverlay.renderThreeOverlay();
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
            if (globalThis.arOverlay) {
                globalThis.arOverlay.removeOverlayMesh(key);
            }
        }
    }
}

function clearmarkerCache() {
    for (const marker of globalThis.markerCache) {
        marker.mat.delete();
        for (const rot of marker.rotations) {
            rot.mat.delete();
        }
        if (marker.matchRotations) {
            for (const rot of marker.matchRotations) {
                rot.mat.delete();
            }
        }
    }
    globalThis.markerCache = [];
}

function getExhibitMarkers() {
    if (globalThis.markerCache.length === 0) {
        buildMarkerCache();
    }
    return globalThis.markerCache;
}

function buildMarkerCache(onProgress) {
    clearmarkerCache();

    const markerElements = Array.from(document.querySelectorAll('ar-marker'));
    const total = markerElements.length;
    let done = 0;

    for (const markerEl of markerElements) {
        const start = performance.now();
        const imgEl = markerEl._markerImg;

        if (imgEl && imgEl.complete && imgEl.naturalWidth > 0) {
            const markerMat = cv.imread(imgEl, cv.IMREAD_COLOR);
            if (markerMat.empty()) {
                markerMat.delete();
                console.warn(`[AR] ${markerEl.markerId} marker image empty, skipped`);
            } else {
                cv.resize(markerMat, markerMat, new cv.Size(config.warpSize, config.warpSize));

                const rot90 = new cv.Mat();
                cv.rotate(markerMat, rot90, cv.ROTATE_90_CLOCKWISE);
                const rot180 = new cv.Mat();
                cv.rotate(markerMat, rot180, cv.ROTATE_180);
                const rot270 = new cv.Mat();
                cv.rotate(markerMat, rot270, cv.ROTATE_90_COUNTERCLOCKWISE);

                // Downscaled copies of each rotation used only for the cheap periodic
                // rotation re-check while tracking (full-size mats stay for initial match).
                const matchSize = new cv.Size(config.rotationMatchSize, config.rotationMatchSize);
                const smallBase = new cv.Mat();
                cv.resize(markerMat, smallBase, matchSize);
                const small90 = new cv.Mat();
                cv.resize(rot270, small90, matchSize);
                const small180 = new cv.Mat();
                cv.resize(rot180, small180, matchSize);
                const small270 = new cv.Mat();
                cv.resize(rot90, small270, matchSize);

                globalThis.markerCache.push({
                    id: markerEl.markerId,
                    mat: markerMat,
                    rotations: [
                        { candidateDeg: 0,   mat: markerMat },
                        { candidateDeg: 90,  mat: rot270 },
                        { candidateDeg: 180, mat: rot180 },
                        { candidateDeg: 270, mat: rot90 },
                    ],
                    matchRotations: [
                        { candidateDeg: 0,   mat: smallBase },
                        { candidateDeg: 90,  mat: small90 },
                        { candidateDeg: 180, mat: small180 },
                        { candidateDeg: 270, mat: small270 },
                    ]
                });

                console.log(`[AR] ${markerEl.markerId} OpenCV cache ready in ${Math.round(performance.now() - start)}ms`);
            }
        } else {
            console.warn(`[AR] ${markerEl.markerId} marker image not loaded, skipped`);
        }

        done += 1;
        if (onProgress) onProgress(done / total);
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

    let bestMatch = null;
    if (!globalThis._matchResultScratch) globalThis._matchResultScratch = new cv.Mat();
    const matchResult = globalThis._matchResultScratch;

    for (const marker of markers) {
        for (const rot of marker.rotations) {
            cv.matchTemplate(markerMat, rot.mat, matchResult, cv.TM_CCOEFF_NORMED);
            const confidence = matchResult.data32F[0];

            if (confidence < globalThis.config.matchConfidenceThreshold) {
                continue;
            }

            if (!bestMatch || confidence > bestMatch.confidence) {
                bestMatch = {
                    markerId: marker.id,
                    confidence,
                    rotationDeg: rot.candidateDeg
                };
            }
        }
    }

    return bestMatch;
}

function updateRotationForMarker(markerMat, templateId) {
    const templates = getExhibitMarkers();
    const template = templates.find(t => t.id === templateId);
    if (!template) return null;

    const size = globalThis.config.rotationMatchSize;
    if (!globalThis._rotMatchSrc) globalThis._rotMatchSrc = new cv.Mat();
    if (!globalThis._matchResultScratch) globalThis._matchResultScratch = new cv.Mat();
    const small = globalThis._rotMatchSrc;
    const matchResult = globalThis._matchResultScratch;

    // Downscale the warped marker once, then compare against the matched template's four
    // downscaled rotations. Smaller templates + reused scratch Mats keep this light enough
    // to run while tracking without dropping frames on mobile.
    cv.resize(markerMat, small, new cv.Size(size, size));

    let bestRotation = null;
    for (const rot of template.matchRotations) {
        cv.matchTemplate(small, rot.mat, matchResult, cv.TM_CCOEFF_NORMED);
        const confidence = matchResult.data32F[0];

        if (confidence >= globalThis.config.matchConfidenceThreshold && (!bestRotation || confidence > bestRotation.confidence)) {
            bestRotation = { rotationDeg: rot.candidateDeg, confidence };
        }
    }

    return bestRotation;
}