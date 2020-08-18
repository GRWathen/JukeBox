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
    let video_id = document.getElementById("video_id")
    let videos = document.querySelectorAll(".video");
    let nodes = [...videos];

    for (let i = 0; i < nodes.length; i++) {
        if (nodes[i].attributes["video_id"].nodeValue === video_id.innerText) {
            nodes.splice(i, 1);
            break;
        }
    }

    const ran = Math.floor(Math.random() * nodes.length);
    video_id.innerText = nodes[ran].attributes["video_id"].nodeValue;

    let att = document.createAttribute("id");
    att.value = "video";

    let div = document.createElement("div");
    div.setAttributeNode(att);

    document.getElementById("video").remove();
    video_id.parentNode.insertBefore(div, video_id.nextSibling);
    onYouTubeIframeAPIReady();

    let banner = document.getElementById("videoBanner")
    const title = nodes[ran].innerText;
    const artist = nodes[ran].parentNode.parentNode.attributes["id"].value;
    videoBanner.innerText = `${artist} - ${title}`;
}

function playVideo(videoID) {
    const video = document.getElementById("video");
    video.setAttribute("src", `https://www.youtube.com/embed/${videoID}?autoplay=1`);

    let videoSpan = document.querySelector(`[video_id="${videoID}"]`);
    let banner = document.getElementById("videoBanner")
    const title = videoSpan.innerText;
    const artist = videoSpan.parentNode.parentNode.attributes["id"].value;
    videoBanner.innerText = `${artist} - ${title}`;
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
