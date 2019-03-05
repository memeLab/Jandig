document.getElementsByClassName("screenshot-button")[0].addEventListener("click", function () {
    console.log("AAAAA")
    const scene = document.getElementsByTagName("canvas")[0]
    
    const img = document.createElement('img');
    scene.toBlob(function (blob) {
        console.log(blob)
        img.src = URL.createObjectURL(blob);
        console.log(img)
        // saveAs(blob, "Dashboard.png"); 
    });
    console.log(scene.toDataURL("image/png"))

})