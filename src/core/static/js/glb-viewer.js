/**
 * Shared GLB 3D model viewer using Three.js (ESM, r184).
 *
 * Usage:
 *   import { GLBViewer } from './glb-viewer.js';
 *   var viewer = GLBViewer.init(container, sourceUrl, options);
 *   // Later, to clean up:
 *   viewer.dispose();
 *
 * Options:
 *   - onThumbnailReady(renderer, scene, camera): called after model loads (for thumbnail generation)
 *   - onAnimationsFound(count): called when animations are detected
 *   - onError(error): called on load failure
 */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/GLTFLoader.js';
import { OrbitControls } from 'three/addons/OrbitControls.js';

function init(container, sourceUrl, options) {
    options = options || {};
    let renderer = null;
    let animationFrameId = null;
    let disposed = false;

    function dispose() {
        if (disposed) return;
        disposed = true;
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
            animationFrameId = null;
        }
        if (renderer) {
            renderer.dispose();
            renderer.forceContextLoss();
            renderer = null;
        }
    }

    const width = container.clientWidth || 600;
    const height = container.clientHeight || width;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);

    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.set(0, 0, 5);

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    container.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.enableZoom = true;
    controls.enablePan = true;
    controls.enableRotate = true;

    const ambientLight = new THREE.AmbientLight(0xFFFDD0, 3.5);
    scene.add(ambientLight);

    let mixer = null;
    const timer = new THREE.Timer();

    function animate() {
        if (disposed) return;
        animationFrameId = requestAnimationFrame(animate);
        timer.update();
        const delta = timer.getDelta();
        if (mixer) mixer.update(delta);
        controls.update();
        renderer.render(scene, camera);
    }

    const loader = new GLTFLoader();
    loader.load(
        sourceUrl,
        function (gltf) {
            if (disposed) return;
            scene.add(gltf.scene);

            if (gltf.animations && gltf.animations.length > 0) {
                mixer = new THREE.AnimationMixer(gltf.scene);
                gltf.animations.forEach(function (clip) {
                    mixer.clipAction(clip).play();
                });
                if (options.onAnimationsFound) {
                    options.onAnimationsFound(gltf.animations.length);
                }
            }

            // Auto-scale and center the model
            const box = new THREE.Box3().setFromObject(gltf.scene);
            const center = box.getCenter(new THREE.Vector3());
            const size = box.getSize(new THREE.Vector3());

            gltf.scene.position.sub(center);

            const maxDim = Math.max(size.x, size.y, size.z);
            const scale = 5 / maxDim;
            gltf.scene.scale.setScalar(scale);

            const distance = Math.max(3, maxDim * 2);
            camera.position.set(distance, distance * 0.5, distance);
            camera.lookAt(0, 0, 0);

            controls.target.set(0, 0, 0);
            controls.update();

            animate();

            if (options.onThumbnailReady) {
                setTimeout(function () {
                    if (disposed) return;
                    renderer.render(scene, camera);
                    options.onThumbnailReady(renderer, scene, camera);
                }, 1000);
            }
        },
        undefined,
        function (error) {
            console.error('Error loading GLB file:', error);
            if (options.onError) {
                options.onError(error);
            }
        }
    );

    return { dispose: dispose };
}

export const GLBViewer = { init: init };
