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
