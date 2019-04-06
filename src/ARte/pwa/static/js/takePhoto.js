function takePicture() {
    const scene = document.getElementsByTagName("canvas")[0]
    const pictureURI = scene.toDataURL("image/png")
    
    let link = document.getElementById("picture-link")
    link.href = pictureURI
    link.download = getPhotoFileName('png')
    link.click()
}

function getPhotoFileName(extension) {
    const date = new Date();
    const day = formatSmallNumber(date.getDate());
    const month = formatSmallNumber(date.getMonth() + 1); // Months are counted from 0-11 here.
    const year = date.getFullYear();
    const hour = formatSmallNumber(date.getHours());
    const minutes = formatSmallNumber(date.getMinutes());
    const seconds = formatSmallNumber(date.getSeconds());
    const milli = date.getMilliseconds();
    return year + month + day + "_" + hour + minutes + seconds + milli + '.' + extension
}

function formatSmallNumber(number) {
    return (number < 10) ? "0" + number : number
}