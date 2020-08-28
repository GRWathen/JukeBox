# World Wide Juke Web
https://world-wide-juke-web.herokuapp.com

[<img src="https://pixabay.com/get/55e0d6404c55b10ff3d89960c62d3e761037d6ec5b59_640.png" width="200"/>](https://pixabay.com/get/55e0d6404c55b10ff3d89960c62d3e761037d6ec5b59_640.png)

**Juke Web** allows _Users_ to save **YouTube** _Video_ links to their personal library for viewing at their convenience, and create _Playlists_ to automatically play through the selected _Videos_.

The **Home** page allows the _User_ to log in, or a new _User_ to register.

_Users_ can add, edit, or delete _Videos_ directly in their libary, or select a _Video_ in their library to watch.

_Users_ are able to enter keywords to search for _Videos_ on **YouTube** and watch them or add them to their library.

The site makes use of the **YouTube Data API** for _Searching_.  
https://developers.google.com/youtube/v3  
Because of API limitations, the _User_ is restricted to **5** searches that return up to **50** _Videos_ per day.

_Users_ may also create _Playlists_ to group multiple _Videos_ from their library to automatically randomly play through the _Videos_ in the _Playlist_.

Because of limited server-side storage capacity, _Users_ are limited to saving **50** _Videos_ in their library, and **5** _Playlists_ capable of having *20* _Videos_ each.

## Technologies
* HTML
* CSS
* JavaScript
* Python
* Flask
* Jinja
* WTForms
* PostgreSQL
* SQLAlchemy
* Heroku
