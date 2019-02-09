function createMarkerFile() {
    // create absoluteBaseURL
    var link = document.createElement('a')
    link.href = ARjs.Context.baseURL
    var absoluteBaseURL = link.href

    // create the base file
    var file = {
        meta: {
            createdBy: 'ARte ' + ARjs.Context.REVISION + ' - Teste Markers',
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
    if (trackingBackend === 'artoolkit') {
        file.subMarkersControls[0].parameters.type = 'pattern'
        file.subMarkersControls[0].parameters.patternUrl = absoluteBaseURL + 'patts/pattern-letterC.patt'
        file.subMarkersControls[1].parameters.type = 'pattern'
        file.subMarkersControls[1].parameters.patternUrl = absoluteBaseURL + 'patts/pattern-kanji.patt'
        file.subMarkersControls[2].parameters.type = 'pattern'
        file.subMarkersControls[2].parameters.patternUrl = absoluteBaseURL + 'patts/pattern-letterF.patt'
        file.subMarkersControls[3].parameters.type = 'pattern'
        file.subMarkersControls[3].parameters.patternUrl = absoluteBaseURL + 'patts/pattern-hiro.patt'
    } else console.assert(false)

    // json.strinfy the value and store it in localStorage
    return file
}

const file = createMarkerFile();
console.table(file.subMarkersControls)
localStorage.setItem('ARjsMultiMarkerFile', JSON.stringify(file))