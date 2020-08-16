"use strict";

// Execute once when DOM is loaded.
document.addEventListener("DOMContentLoaded", function (event) {
    //$(function () { // jQuery
    console.log("Playlist DOM loaded");
});

// Execute once when window is loaded and rendered.
window.addEventListener("load", function (event) {
    //$(document).ready(function () { // jQuery
    console.log("Playlist Window loaded");
});

console.log("playlist.js")

// https://developers.google.com/youtube/iframe_api_reference

let player;
function onYouTubeIframeAPIReady() {
    const video_id = document.getElementById("video_id").innerText;
    player = new YT.Player("video", {
        videoId: video_id,
        frameborder: "0",
        allowfullscreen: "1",
        allow: "accelerometer; autoplay; encrypted-media; picture-in-picture",
        title: "video player",
        width: "auto",
        height: "auto",
        events: {
            "onReady": onPlayerReady,
            "onStateChange": onPlayerStateChange
        }
    });
}

function onPlayerReady(event) {
    event.target.playVideo();
}

function onPlayerStateChange(event) {
    if (event.data === 0) {
        let video_id = document.getElementById("video_id");
        video_id.innerText = playPlaylist(video_id.innerText);

        document.getElementById("video").remove();

        let att = document.createAttribute("id");
        att.value = "video";

        let div = document.createElement("div");
        div.setAttributeNode(att);

        video_id.parentNode.insertBefore(div, video_id.nextSibling);
        onYouTubeIframeAPIReady();
    }
}
