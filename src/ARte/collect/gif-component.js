

AFRAME.registerComponent('gif', {
    schema: {
        src: { type: 'string', default: '' },
        marker: { default: '' },
        position: { default: '0 0 0' },
        rotation: { default: '270 0 0' },
        scale: { default: '1 1' },
    },

    init: function() {
        var self = this

        this.worker = new Worker('static/js/fetch-worker.js')

        this.worker.postMessage(this.data.src);

        this.gif = null;
        this.frames = null;


        this.worker.addEventListener('message', function(e) {
            // console.log('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' + e.data)
            self.gif = new GIF(e.data)
            self.gifLoaded = true
            // self.frames = self.gif.decompressFrames(true)
        })

        this.gifDecompressed = true;
        this.gifLoaded = false;
        this.gifPlaying = false;

        this.canvas = document.createElement('canvas');
        this.canvas.setAttribute('id', this.data.src)

        this.el.setAttribute('draw-canvas', this.canvas)
        this.el.setAttribute('material', {src: this.canvas})
        this.el.setAttribute('geometry', {primitive: 'plane'})

        this.el.setAttribute('rotation', this.data.rotation)
        this.el.setAttribute('position', this.data.position)
        this.el.setAttribute('scale', this.data.scale)

        this.marker = document.querySelector(this.data.marker);
        
        this.marker.addEventListener('markerFound', function(e) {
            self.playGIF()
        })

        this.marker.addEventListener('markerLost', function(e) {
            self.stopGIF()
        })
    },

    decompressGif : function() {
        if(this.gifLoaded && !this.gifDecompressed) {
            // console.log(this.gif)
            this.gifDecompressed = true
            this.frames = this.gif.decompressFrames(true)
            console.log(this.frames)
        }
    },

    fetchGif : function() {
        if(!this.gifLoaded) {
            this.gif = fetch(this.data.src)
            .then(resp => resp.arrayBuffer())
            .then(buff => new GIF(buff))
            .then(this.gifLoaded = true);

            this.frames = this.gif.then(gif => gif.decompressFrames(true))
        }
    },

    playGIF : function() {
        // this.fetchGif();
        this.decompressGif();
        this.gifPlaying = true;
        this.renderGIF(this.frames, 0);
        // this.frames.then(frames => this.renderGIF(frames, 0));
    },

    stopGIF : function() {
        this.gifPlaying = false;
    },

    renderGIF : function(frames, frameIndex) {
        if(this.gifPlaying) {
            if (frameIndex >= frames.length) {
                frameIndex = 0;
            }
            var frame = frames[frameIndex]
            var start = new Date().getTime();
        
            if(frameIndex != 0) {
                var lastFrame = frames[frameIndex - 1]
                if(lastFrame.disposalType == 2) {
                    this.canvas.getContext('2d').clearRect(0, 0, this.canvas.width, this.canvas.height);
        
                }
            } else {
                this.canvas.width = frame.dims.width;
                this.canvas.height = frame.dims.height;
            }

            this.drawGIF(frame);
        
            var end = new Date().getTime();
        
            var timeDiff = end - start;
        
            var self = this
  
            setTimeout(function() {
                self.renderGIF(frames, frameIndex+1);
            }, Math.max(0, Math.floor(frame.delay - timeDiff)));
        }
    },
    
    drawGIF : function(frame) {
        var tmpCanvas = document.createElement('canvas');
        
        tmpCanvas.width = frame.dims.width;
        tmpCanvas.height = frame.dims.height;
  
        var tmpCtx = tmpCanvas.getContext('2d');
        var mainCtx = this.canvas.getContext('2d');

        var frameImageData = tmpCtx.createImageData(frame.dims.width, frame.dims.height);
        frameImageData.data.set(frame.patch);

        tmpCtx.putImageData(frameImageData, 0, 0);

        mainCtx.drawImage(tmpCanvas, frame.dims.left, frame.dims.top);
    }
})