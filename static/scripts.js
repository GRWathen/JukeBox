"use strict";

// Execute once when DOM is loaded.
document.addEventListener("DOMContentLoaded", function (event) {
//$(function () { // jQuery
    console.log("DOM loaded");
});

// Execute once when window is loaded and rendered.
window.addEventListener("load", function (event) {
//$(document).ready(function () { // jQuery
    console.log("Window loaded");
});

function toggleArtist(elem) {
    const videos = elem.parentNode.getElementsByTagName("ul")[0].getElementsByTagName("li");
    for (let i=0; i<videos.length; i++) {
        videos[i].classList.toggle("hidden");
    }
}

function playVideo(videoID) {
    const video = document.getElementById("video");
    video.setAttribute("src", `https://www.youtube-nocookie.com/embed/${videoID}?autoplay=1`);
}

async function deleteVideo(elem, id) {
    const response = await axios.post(`/videos/${id}/delete`);
    if (response.data != "OK") {
        return;
    }
    const item = elem.parentNode;
    const list = item.parentNode.parentNode;
    item.remove();
    if (list.getElementsByTagName("li").length === 0) {
        list.remove();
    }
}
