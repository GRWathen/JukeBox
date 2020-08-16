"use strict";

// Execute once when DOM is loaded.
document.addEventListener("DOMContentLoaded", function (event) {
    //$(function () { // jQuery
    console.log("YouTube DOM loaded");
});

// Execute once when window is loaded and rendered.
window.addEventListener("load", function (event) {
    //$(document).ready(function () { // jQuery
    console.log("YouTube Window loaded");

    // https://www.youtube.com/iframe_api

    if (!window['YT']) { var YT = { loading: 0, loaded: 0 }; } if (!window['YTConfig']) { var YTConfig = { 'host': 'http://www.youtube.com' }; } if (!YT.loading) { YT.loading = 1; (function () { var l = []; YT.ready = function (f) { if (YT.loaded) { f(); } else { l.push(f); } }; window.onYTReady = function () { YT.loaded = 1; for (var i = 0; i < l.length; i++) { try { l[i](); } catch (e) { } } }; YT.setConfig = function (c) { for (var k in c) { if (c.hasOwnProperty(k)) { YTConfig[k] = c[k]; } } }; var a = document.createElement('script'); a.type = 'text/javascript'; a.id = 'www-widgetapi-script'; a.src = 'https://s.ytimg.com/yts/jsbin/www-widgetapi-vfldn1jRM/www-widgetapi.js'; a.async = true; var c = document.currentScript; if (c) { var n = c.nonce || c.getAttribute('nonce'); if (n) { a.setAttribute('nonce', n); } } var b = document.getElementsByTagName('script')[0]; b.parentNode.insertBefore(a, b); })(); }
});

console.log("youtube.js")
