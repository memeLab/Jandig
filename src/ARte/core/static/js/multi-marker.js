function createMarkerFile() {
    var absoluteBaseURL = window.location
    // create the base file
    var file = {
        meta: {
            createdAt: new Date().toJSON(),
        },
        subMarkersControls: [
            // empty for now... being filled 
        ]
    }
    // add a subMarkersControls
    for (let i = 0; i < 4; i++) {
        file.subMarkersControls[i] = {
            parameters: {},
            poseMatrix: new THREE.Matrix4().makeTranslation(0, 0, 0).toArray(),
        }
    }
    file.subMarkersControls[0].parameters.type = 'pattern'
    file.subMarkersControls[0].parameters.patternUrl = absoluteBaseURL + 'static/patts/pattern-letterC.patt'
    file.subMarkersControls[1].parameters.type = 'pattern'
    file.subMarkersControls[1].parameters.patternUrl = absoluteBaseURL + 'static/patts/pattern-kanji.patt'
    file.subMarkersControls[2].parameters.type = 'pattern'
    file.subMarkersControls[2].parameters.patternUrl = absoluteBaseURL + 'static/patts/pattern-letterF.patt'
   
    return file
}

const file = createMarkerFile();
localStorage.setItem('ARjsMultiMarkerFile', JSON.stringify(file))