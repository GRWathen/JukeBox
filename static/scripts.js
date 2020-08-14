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

function checkboxArtist(elem) {
    const videos = elem.parentNode.getElementsByTagName("ul")[0].getElementsByTagName("li");
    for (let i = 0; i < videos.length; i++) {
        const checkbox = videos[i].getElementsByTagName("input")[0]
        checkbox.checked = elem.checked;
    }
}

function playPlaylist() {
}

function playVideo(videoID) {
    const video = document.getElementById("video");
    video.setAttribute("src", `https://www.youtube-nocookie.com/embed/${videoID}?autoplay=1`);
}

async function trashPlaylist(elem) {
    const item = elem.parentNode;
    deletePlaylist(item);
}

async function trashVideo(elem) {
    const item = elem.parentNode;
    deleteVideo(item);
}

async function deletePlaylist(item) {
    const id = item.getAttribute("data-ID")
    const response = await axios.post(`/playlists/${id}/delete`);
    if (response.data != "OK") {
        return false;
    }
    item.remove();
    return true;
}

async function deleteVideo(item) {
    const id = item.getAttribute("data-ID")
    const response = await axios.post(`/videos/${id}/delete`);
    if (response.data != "OK") {
        return false;
    }

    const list = item.parentNode.parentNode;
    item.remove();
    if (list.getElementsByTagName("li").length === 0) {
        list.remove();
    }

    return true;
}

async function trashArtist(elem) {
    const videos = elem.parentNode.getElementsByTagName("ul")[0].getElementsByTagName("li");
    for (let i=0; i<videos.length; i++) {
        const item = videos[i];
        deleteVideo(item);
    }
}
