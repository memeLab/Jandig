   
/* Web worker for download the gif in background */

self.addEventListener('message', function(e) {
    const buff = fetch('/' + e.data)
                    .then(resp => resp.arrayBuffer())
                    .then(buff => self.postMessage(buff))
})
