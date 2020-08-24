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
        const checkbox = videos[i].getElementsByTagName("input")[0];
        checkbox.checked = elem.checked;
    }
}

function playPlaylist() {
    let video_id = document.getElementById("video_id");
    let videos = document.querySelectorAll(".video");
    let nodes = [...videos];
    let node = nodes[0];

    if (nodes.length > 1) {
        for (let i = 0; i < nodes.length; i++) {
            if (nodes[i].attributes["video_id"].nodeValue === video_id.innerText) {
                nodes.splice(i, 1);
                break;
            }
        }
        const ran = Math.floor(Math.random() * nodes.length);
        node = nodes[ran];
    }

    video_id.innerText = node.attributes["video_id"].nodeValue;

    let att = document.createAttribute("id");
    att.value = "video";

    let div = document.createElement("div");
    div.setAttributeNode(att);

    document.getElementById("video").remove();
    video_id.parentNode.insertBefore(div, video_id.nextSibling);
    onYouTubeIframeAPIReady();

    let banner = document.getElementById("videoBanner");
    const title = node.innerText;
    const artist = node.parentNode.parentNode.attributes["id"].value;
    videoBanner.innerText = `${artist} - ${title}`;
}

function playVideo(videoID) {
    const video = document.getElementById("video");
    video.setAttribute("src", `https://www.youtube.com/embed/${videoID}?autoplay=1`);

    let videoSpan = document.querySelector(`[video_id="${videoID}"]`);
    let banner = document.getElementById("videoBanner");
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
    const id = item.getAttribute("data-ID");
    const response = await axios.post(`/playlists/${id}/delete`);
    if (response.data != "OK") {
        return false;
    }

    item.remove();

    let count = document.getElementById("playlistCount");
    let i = parseInt(count.innerText, 10) - 1;
    count.innerText = i.toString();

    return true;
}

async function deleteVideo(item) {
    const id = item.getAttribute("data-ID");
    const response = await axios.post(`/videos/${id}/delete`);
    if (response.data != "OK") {
        return false;
    }

    const list = item.parentNode.parentNode;
    item.remove();

    let count = document.getElementById("videoCount");
    let i = parseInt(count.innerText, 10) - 1;
    count.innerText = i.toString();

    if (list.getElementsByTagName("li").length === 0) {
        let library = list.parentNode;
        list.remove();
        if (library.getElementsByTagName("li").length === 0) {
            library.remove();
        }
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

function shiftVideos(direction) {
    let thumbnails = document.getElementById("thumbnails").getElementsByClassName("searchThumbnail");

    if (direction === -1) {
        let item = thumbnails[thumbnails.length-1].cloneNode(true);
        thumbnails[thumbnails.length-1].remove();
        document.getElementById("thumbnails").prepend(item);
    }
    else {
        let item = thumbnails[0].cloneNode(true);
        thumbnails[0].remove();
        document.getElementById("thumbnails").append(item);
    }
}
