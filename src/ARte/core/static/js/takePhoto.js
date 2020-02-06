function takePicture() {


    const scene = document.getElementsByTagName("canvas")[0];
    var ctx = scene.getContext("2d");

    pictureURI = scene.toDataURL("image/png");
    var image = new Image();
    image.src = pictureURI;

    flipImage(image);
    
}

function flipImage(image){
  var myCanvas=document.createElement("canvas");
  var myCanvasContext=myCanvas.getContext("2d");

  var imgWidth=image.width;
  var imgHeight=image.height;
  myCanvas.width= imgWidth;
  myCanvas.height=imgWidth;

  myCanvasContext.drawImage(image,0,0);
  myCanvasContext.clearRect(0,0,myCanvas.width,myCanvas.height);
  myCanvasContext.save();
  myCanvasContext.translate(myCanvas.width/2,myCanvas.height/2);
  myCanvasContext.rotate(-90*Math.PI/180);
  myCanvasContext.drawImage(image,-image.width/2,-image.width/2);
  myCanvasContext.restore();
  var imageData=myCanvasContext.getImageData(0,0, imgHeight, imgWidth);
  myCanvas.width= imgHeight;

  myCanvasContext.putImageData(imageData,0,0,0,0, imageData.width, imageData.height);
  let link = document.getElementById("picture-link");
  link.href = myCanvas.toDataURL("image/png");
  link.download = getPhotoFileName('png');
  link.click();
  myCanvasContext.restore();
  

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
