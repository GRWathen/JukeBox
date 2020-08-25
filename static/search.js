"use strict";

// Execute once when DOM is loaded.
document.addEventListener("DOMContentLoaded", function (event) {
    //$(function () { // jQuery
    console.log("Search DOM loaded");
});

// Execute once when window is loaded and rendered.
window.addEventListener("load", function (event) {
    //$(document).ready(function () { // jQuery
    console.log("Search Window loaded");
});

console.log("search.js")

function shiftVideos(direction) {
    let thumbnails = document.getElementById("thumbnails").getElementsByClassName("searchThumbnail");

    if (direction === -1) {
        let item = thumbnails[thumbnails.length - 1].cloneNode(true);
        thumbnails[thumbnails.length - 1].remove();
        document.getElementById("thumbnails").prepend(item);
    }
    else {
        let item = thumbnails[0].cloneNode(true);
        thumbnails[0].remove();
        document.getElementById("thumbnails").append(item);
    }
}
