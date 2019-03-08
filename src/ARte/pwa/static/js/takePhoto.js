document.getElementsByClassName("screenshot-button")[0].addEventListener("click", function () {
    const scene = document.getElementsByTagName("canvas")[0]
    const photoDataURI = scene.toDataURL("image/png")

    var link = document.createElement('a');

    link.download = getPhotoFileName() + '.png';
    link.href = photoDataURI;
    link.click();
})

function getPhotoFileName() {
    const date = new Date();
    const day = formatSmallNumber(date.getDate());
    const month = formatSmallNumber(date.getMonth() + 1); // Months are counted from 0-11 here.
    const year = date.getFullYear();
    const hour = formatSmallNumber(date.getHours());
    const minutes = formatSmallNumber(date.getMinutes());
    const seconds = formatSmallNumber(date.getSeconds());
    const milli = date.getMilliseconds();
    return year + month + day + "_" + hour + minutes + seconds + milli
}

function formatSmallNumber(number) {
    return (number < 10) ? "0" + number : number
}