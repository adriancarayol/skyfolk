var overlay = document.getElementById('video');
var video = document.getElementById('video');
var videoPlaying = false;
overlay.onclick = function() {
    if (videoPlaying) {
        video.pause();
        videoPlaying = false;
    }
    else {
        video.play();
        videoPlaying = true;
    }
}