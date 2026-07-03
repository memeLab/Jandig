/**
 * Shared GLB 3D model viewer using Three.js.
 *
 * Usage:
 *   var viewer = GLBViewer.init(container, sourceUrl, options);
 *   // Later, to clean up:
 *   viewer.dispose();
 *
 * Options:
 *   - onThumbnailReady(blob, renderer, scene, camera): called after model loads (for thumbnail generation)
 *   - onAnimationsFound(count): called when animations are detected
 *   - onError(error): called on load failure
 */
var GLBViewer = (function () {
    var THREE_VERSION = '0.127.0';
    var THREE_BASE = 'https://unpkg.com/three@' + THREE_VERSION;

    function loadThree() {
        if (window.THREE) return Promise.resolve();
        return new Promise(function (resolve, reject) {
            var script = document.createElement('script');
            script.src = THREE_BASE + '/build/three.min.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    function init(container, sourceUrl, options) {
        options = options || {};
        var renderer = null;
        var animationFrameId = null;
        var disposed = false;

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

        loadThree().then(function () {
            if (disposed) return;
            return Promise.all([
                import(THREE_BASE + '/examples/jsm/loaders/GLTFLoader.js'),
                import(THREE_BASE + '/examples/jsm/controls/OrbitControls.js')
            ]);
        }).then(function (modules) {
            if (disposed) return;
            var GLTFLoader = modules[0].GLTFLoader;
            var OrbitControls = modules[1].OrbitControls;

            var width = container.clientWidth || 600;
            var height = container.clientHeight || width;

            var scene = new THREE.Scene();
            scene.background = new THREE.Color(0xf0f0f0);

            var camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
            camera.position.set(0, 0, 5);

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(width, height);
            container.appendChild(renderer.domElement);

            var controls = new OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.enableZoom = true;
            controls.enablePan = true;
            controls.enableRotate = true;

            var ambientLight = new THREE.AmbientLight(0xFFFDD0, 3.5);
            scene.add(ambientLight);

            var mixer = null;
            var clock = new THREE.Clock();

            function animate() {
                if (disposed) return;
                animationFrameId = requestAnimationFrame(animate);
                var delta = clock.getDelta();
                if (mixer) mixer.update(delta);
                controls.update();
                renderer.render(scene, camera);
            }

            var loader = new GLTFLoader();
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
                    var box = new THREE.Box3().setFromObject(gltf.scene);
                    var center = box.getCenter(new THREE.Vector3());
                    var size = box.getSize(new THREE.Vector3());

                    gltf.scene.position.sub(center);

                    var maxDim = Math.max(size.x, size.y, size.z);
                    var scale = 5 / maxDim;
                    gltf.scene.scale.setScalar(scale);

                    var distance = Math.max(3, maxDim * 2);
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
        }).catch(function (error) {
            console.error('Error initializing GLB viewer:', error);
            if (options.onError) {
                options.onError(error);
            }
        });

        return { dispose: dispose };
    }

    return { init: init };
})();
