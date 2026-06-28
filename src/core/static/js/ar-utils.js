async function startCamera() {
    const userCamera = document.getElementById('camera');
    try {
        mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
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

function CheckOpenCvIsReady() {
    if (!window.cv) {
        console.error('OpenCV failed to load.');
        return;
    }
    startCamera();
}