# TODO: Why is there a ROLLBACK?!

from flask import Flask, request, render_template, redirect, session, flash, make_response
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Video, Playlist, Playlists_Videos
from forms import AddPlaylistForm, AddPlaylistButtonForm, AddVideoForm, AddVideoButtonForm, EditUserForm, EditPlaylistForm, EditPlaylistButtonForm, EditVideoForm, EditVideoButtonForm, LogInOutForm, RegisterForm, SearchForm
from wtforms import BooleanField
from secrets import SECRET_KEY, SECRET_API_KEY

import datetime, random, requests

MAX_VIDEOS = 50
MAX_PLAYLISTS = 5
VIDEOS_PLAYLIST = 20
MAX_SEARCHES = 5

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///JukeBoxDB"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
#app.config["TESTING"] = True
#app.config["DEBUG_TB_HOSTS"] = ["dont-show-debug-toolbar"]
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
#debug = DebugToolbarExtension(app)

connect_db(app)

@app.route("/favicon.ico")
def fav_icon():
    """Favorite Icon"""
    return ""

@app.route("/", methods=["GET", "POST"], defaults={"path": ""})
@app.route("/<path>")
def homepage(path):
    """Show homepage"""
    form_log = LogInOutForm()
    form_add_playlist_button = AddPlaylistButtonForm()
    form_add_video_button = AddVideoButtonForm()
    form_edit_playlist_button = EditPlaylistButtonForm()
    form_edit_video_button = EditVideoButtonForm()

    playlists = None
    playlist_count = 0
    videos = None
    video_count = 0
    searches = 0
    if session.get("user_id"):
        playlists = Playlist.query.filter(Playlist.user_id == session["user_id"]).order_by(Playlist.name.asc()).all()
        playlist_count = len(playlists)
        videos = Video.query.filter(Video.user_id == session["user_id"]).order_by(Video.artist.asc(), Video.title.asc()).all()
        video_count = len(videos)
        user = User.query.get(session.get("user_id"))
        searches = MAX_SEARCHES - user.searches

    return render_template("/extends/home.html", FORM_LOG=form_log, USER_ID=session.get("user_id"), VIDEO=None, VIDEOS=videos, MAX_VIDEOS=MAX_VIDEOS, VIDEO_COUNT=video_count, PLAYLISTS=playlists, MAX_PLAYLISTS=MAX_PLAYLISTS, PLAYLIST_COUNT=playlist_count, SEARCHES=searches, LIBRARY_NAME=None, FORM_ADD_PLAYLIST_BUTTON=form_add_playlist_button, FORM_ADD_VIDEO_BUTTON=form_add_video_button, FORM_EDIT_PLAYLIST_BUTTON=form_edit_playlist_button, FORM_EDIT_VIDEO_BUTTON=form_edit_video_button, FROM_ROUTE="/")

# ---------- REGISTER / LOGIN / LOGOUT ----------

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user: produce form & handle form submission."""
    form_log = LogInOutForm()
    form_register = RegisterForm()

    if form_register.validate_on_submit():
        error = False

        name = form_register.username.data
        if name is None or len(name) == 0:
            error = True
            form_register.username.errors.append("Username may not be blank")
        
        pwd = form_register.password.data
        if pwd is None or len(pwd) == 0:
            error = True
            form_register.password.errors.append("Password may not be blank")
        
        confirm = form_register.confirm.data
        if confirm != pwd:
            error = True
            form_register.confirm.errors.append("Confirm Password and Password must be the same")
        
        # TODO: Validate email
        email = form_register.email.data
        if email is None or len(email) == 0:
            error = True
            form_register.email.errors.append("Email may not be blank")
        
        pacode = form_register.public_access_code.data
        if pacode is None or len(pacode) == 0:
            pacode = None
        
        if error:
            return render_template("register.html", FORM_LOG=form_log, FORM_REGISTER=form_register, FROM_ROUTE="/register")

        user = User.register(name, pwd, email, pacode, 0, datetime.datetime.now())
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            if len(e.orig.args) > 0:
                lst = e.orig.args[0].split("=")
                if len(lst) == 2 and lst[1].startswith("(") and lst[1].endswith(") already exists.\n"):
                    flash(lst[1])
                else:
                    flash("ERROR")
            else:
                flash("ERROR")
            #...\nDETAIL:  Key (username)=(one) already exists.\n
            #...\nDETAIL:  Key (email)=(a@b.c) already exists.\n
            #...\nDETAIL:  Key (public_access_code)=(pac) already exists.\n
            return render_template("register.html", FORM_LOG=form_log, FORM_REGISTER=form_register, FROM_ROUTE="/register")
        except Exception:
            db.session.rollback()
            flash("ERROR")
            return render_template("register.html", FORM_LOG=form_log, FORM_REGISTER=form_register, FROM_ROUTE="/register")

        session["username"] = user.username
        session["user_id"] = user.id
        # on successful login, redirect to secret page
        flash("Logged In")
        return redirect("/")
    else:
        return render_template("register.html", FORM_LOG=form_log, FORM_REGISTER=form_register, FROM_ROUTE="/register")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Produce login form or handle login."""
    error = False
    form_log = LogInOutForm()
    from_route = request.form.get("from_route")
    if from_route is None or len(from_route) == 0:
        from_route = "/"

    name = request.form.get("log_username")
    if name is None or len(name) == 0:
        error = True
        flash("Username may not be blank")
    
    pwd = request.form.get("log_password")
    if pwd is None or len(pwd) == 0:
        error = True
        flash("Password may not be blank")
    
    if error:
        return redirect(from_route)
    
    if form_log.validate_on_submit():
        # authenticate will return a user or False
        user = User.authenticate(name, pwd)
        if user:
            session["username"] = user.username
            session["user_id"] = user.id
            flash("Logged In")
            return redirect("/")
        else:
            flash("Invalid Username and/or Password")

    return redirect(from_route)

@app.route("/logout", methods=["POST"])
def logout():
    """Logs user out and redirects to homepage."""
    if session.get("username"):
        session.pop("username")
        session.pop("user_id")
        flash("Logged Out")
    return redirect("/")

# ==================================================

# -------------------- USERS --------------------

@app.route("/users/<int:id>/edit", methods=["GET", "POST"])
def edit_user(id):
    """Edit user"""
    if not session.get("username"):
        flash("You must be logged in")
        return redirect("/")
    if id != session.get("user_id"):
        flash("Invalid user")
        return redirect("/")

    user = None
    try:
        user = User.query.get(id)
        if user is None:
            flash("None Exception")
            return redirect("/")
    except Exception:
        flash("Edit User Error")
        return redirect("/")

    form = EditUserForm(obj=user)
    if form.validate_on_submit():
        try:
            form.populate_obj(user)
            db.session.add(user)
            db.session.commit()

            flash(f"{user.username} edited")
            return redirect("/")
        except IntegrityError as e:
            db.session.rollback()
            if len(e.orig.args) > 0:
                flash(f"args:[{e.orig.args}]")
            else:
                flash("ERROR")
            return render_template("edit_user.html", FORM=form, USER_ID=id, USERNAME=user.username, FROM_ROUTE=f"/users/{id}/edit")
        except Exception:
            db.session.rollback()
            flash("ERROR")
            return render_template("edit_user.html", FORM=form, USER_ID=id, USERNAME=user.username, FROM_ROUTE=f"/users/{id}/edit")
    else:
        return render_template("edit_user.html", FORM=form, USER_ID=id, USERNAME=user.username, FROM_ROUTE=f"/users/{id}/edit")

# ==================================================

# -------------------- PLAYLISTS --------------------

@app.route("/playlists/<int:id>")
def watch_playlist(id):
    """Watch playlist"""
    if not session.get("username"):
        flash("You must be logged in")
        return redirect("/")

    playlists = None
    searches = 0
    try:
        playlist = Playlist.query.get(id)
        if playlist is None:
            raise Exception("None Exception")
        if playlist.user_id != session.get("user_id"):
            raise Exception("Invalid User")
        user = User.query.get(session.get("user_id"))
        searches = MAX_SEARCHES - user.searches
    except Exception:
        flash("Watch Playlist Error")
        return redirect("/")

    form_log = LogInOutForm()
    form_add_playlist_button = AddPlaylistButtonForm()
    form_add_video_button = AddVideoButtonForm()
    form_edit_playlist_button = EditPlaylistButtonForm()
    form_edit_video_button = EditVideoButtonForm()

    playlists = Playlist.query.filter(Playlist.user_id == session["user_id"]).order_by(Playlist.name.asc()).all()
    playlist = Playlist.query.get(id)

    videos = playlist.videos
    video = videos[random.randrange(0, len(videos))]

    playlist_count = len(playlists)
    video_count = len(Video.query.filter(Video.user_id == session["user_id"]).order_by(Video.artist.asc(), Video.title.asc()).all())

    return render_template("/extends/playlist.html", FORM_LOG=form_log, USER_ID=session.get("user_id"), VIDEO=video, VIDEOS=videos, MAX_VIDEOS=MAX_VIDEOS, VIDEO_COUNT=video_count, PLAYLISTS=playlists, MAX_PLAYLISTS=MAX_PLAYLISTS, PLAYLIST_COUNT=playlist_count, SEARCHES=searches, LIBRARY_NAME=playlist.name, FORM_ADD_PLAYLIST_BUTTON=form_add_playlist_button, FORM_ADD_VIDEO_BUTTON=form_add_video_button, FORM_EDIT_PLAYLIST_BUTTON=form_edit_playlist_button, FORM_EDIT_VIDEO_BUTTON=form_edit_video_button, FROM_ROUTE="/playlists/{id}")

@app.route("/playlists/new", methods=["GET", "POST"])
def add_playlist():
    """Add playlist"""
    if not session.get("username"):
        flash("You must be logged in")
        return redirect("/")

    playlists = Playlist.query.filter(Playlist.user_id == session["user_id"]).order_by(Playlist.name.asc()).all()
    if (len(playlists) >= MAX_PLAYLISTS):
        flash(f"Maximum of {MAX_PLAYLISTS} playlists reached")
        return redirect("/")

    videos = Video.query.filter(Video.user_id == session["user_id"]).order_by(Video.artist.asc(), Video.title.asc()).all()

    CopyOfAddPlaylistForm = type('CopyOfAddPlaylistForm', AddPlaylistForm.__bases__, dict(AddPlaylistForm.__dict__))

    artist = None
    for video in videos:
        if video.artist != artist:
            artist = video.artist
            setattr(CopyOfAddPlaylistForm, "[" + artist + "]", BooleanField(artist))
        setattr(CopyOfAddPlaylistForm, str(video.id), BooleanField(video.title))
    form = CopyOfAddPlaylistForm()

    if form.validate_on_submit():
        try:
            playlist = Playlist(
                user_id=session["user_id"],
                name=form.name.data)
            db.session.add(playlist)
            db.session.commit()

            count = 0
            for key, value in form.data.items():
                if not key.isdigit():
                    continue
                if not value:
                    continue
                join = Playlists_Videos(
                    playlist_id=playlist.id,
                    video_id=int(key))
                db.session.add(join)
                count = count + 1

            if count == 0:
                db.session.rollback()
                db.session.delete(playlist)
                db.session.commit()
                flash(f"Select videos")
                return redirect("/playlists/new")
            if count > VIDEOS_PLAYLIST:
                db.session.rollback()
                db.session.delete(playlist)
                db.session.commit()
                flash(f"Maximum {VIDEOS_PLAYLIST} allowed videos exceeded")
                return redirect("/playlists/new")

            flash(f"{form.name.data} added")
            db.session.commit()

            return redirect("/")
        except IntegrityError as e:
            db.session.rollback()
            if len(e.orig.args) > 0:
                flash(f"args:[{e.orig.args}]")
            else:
                flash("ERROR")
            return render_template("add_playlist.html", FORM=form, VIDEOS=videos, FROM_ROUTE="/playlists/new")
        except Exception:
            db.session.rollback()
            flash("ERROR")
            return render_template("add_playlist.html", FORM=form, VIDEOS=videos, FROM_ROUTE="/playlists/new")
    else:
        return render_template("add_playlist.html", FORM=form, VIDEOS=videos, FROM_ROUTE="/playlists/new")

@app.route("/playlists/<int:id>/edit", methods=["GET", "POST"])
def edit_playlist(id):
    """Edit playlist"""
    if not session.get("username"):
        flash("You must be logged in")
        return redirect("/")

    playlist = None
    try:
        playlist = Playlist.query.get(id)
        if playlist is None:
            raise Exception("None Exception")
        if playlist.user_id != session.get("user_id"):
            raise Exception("Invalid User")
    except Exception:
        flash("Edit Playlist Error")
        return redirect("/")

    video_IDs = set(())
    for video in playlist.videos:
        video_IDs.add(video.id)

    videos = Video.query.filter(Video.user_id == session["user_id"]).order_by(Video.artist.asc(), Video.title.asc()).all()

    CopyOfEditPlaylistForm = type('CopyOfEditPlaylistForm', EditPlaylistForm.__bases__, dict(EditPlaylistForm.__dict__))

    artist = None
    for video in videos:
        if video.artist != artist:
            artist = video.artist
            setattr(CopyOfEditPlaylistForm, "[" + artist + "]", BooleanField(artist))
        if video.id in video_IDs:
            setattr(CopyOfEditPlaylistForm, str(video.id), BooleanField(video.title, default="checked"))
        else:
            setattr(CopyOfEditPlaylistForm, str(video.id), BooleanField(video.title))
    form = CopyOfEditPlaylistForm(obj=playlist)

    if form.validate_on_submit():
        try:
            playlist.name = form.name.data

            count = 0
            for key, value in form.data.items():
                if not key.isdigit():
                    continue
                if not value:
                    continue

                video_id = int(key)
                count = count + 1
                if video_id in video_IDs:
                    video_IDs.remove(video_id)
                    continue

                join = Playlists_Videos(
                    playlist_id=playlist.id,
                    video_id=video_id)
                db.session.add(join)

            for video_id in video_IDs.copy():
                p_v = Playlists_Videos.query.filter(Playlists_Videos.playlist_id == playlist.id, Playlists_Videos.video_id == video_id).first()
                if p_v is not None:
                    db.session.delete(p_v)
                video_IDs.remove(video_id)

            if count > VIDEOS_PLAYLIST:
                db.session.rollback()
                flash(f"Maximum {VIDEOS_PLAYLIST} allowed videos exceeded")
                return redirect(f"/playlists/{id}/edit")

            db.session.commit()
            flash(f"{form.name.data} edited")

            return redirect("/")
        except IntegrityError as e:
            db.session.rollback()
            if len(e.orig.args) > 0:
                flash(f"args:[{e.orig.args}]")
            else:
                flash("ERROR")
            return render_template("edit_playlist.html", FORM=form, VIDEOS=videos, PLAYLIST_ID=id, FROM_ROUTE=f"/playlist/{id}/edit")
        except Exception as e:
            db.session.rollback()
            flash("ERROR")
            return render_template("edit_playlist.html", FORM=form, VIDEOS=videos, PLAYLIST_ID=id, FROM_ROUTE=f"/playlist/{id}/edit")
    else:
        return render_template("edit_playlist.html", FORM=form, VIDEOS=videos, PLAYLIST_ID=id, FROM_ROUTE=f"/playlists/{id}/edit")

@app.route("/playlists/<int:id>/delete", methods=["POST"])
def delete_playlist(id):
    """Delete playlist"""
    if not session.get("username"):
        return "You must be logged in"

    try:
        playlist = Playlist.query.get(id)
        if playlist is None:
            raise Exception("None Exception")
        if playlist.user_id != session.get("user_id"):
            raise Exception("Invalid User")

        db.session.delete(playlist)
        db.session.commit()

        return "OK"
    except IntegrityError as e:
        db.session.rollback()
        flash("ERROR")
        return "IntegrityError"
    except Exception as e:
        db.session.rollback()
        flash("ERROR")
        return "Exception"

# ==================================================

# -------------------- VIDEOS --------------------

@app.route("/videos/new", methods=["GET", "POST"])
def add_video():
    """Add video"""
    if not session.get("username"):
        flash("You must be logged in")
        return redirect("/")

    videos = Video.query.filter(Video.user_id == session["user_id"]).order_by(Video.artist.asc(), Video.title.asc()).all()
    if (len(videos) >= MAX_VIDEOS):
        flash(f"Maximum of {MAX_VIDEOS} videos reached")
        return redirect("/")

    form = AddVideoForm()
    if form.validate_on_submit():
        try:
            video = Video(
                user_id=session["user_id"],
                title=form.title.data,
                artist=form.artist.data,
                video_id=form.video_id.data)
            db.session.add(video)
            db.session.commit()

            flash(f"{form.title.data} added")
            return redirect("/")
        except IntegrityError as e:
            db.session.rollback()
            if len(e.orig.args) > 0:
                flash(f"args:[{e.orig.args}]")
            else:
                flash("ERROR")
            return render_template("add_video.html", FORM=form, FROM_ROUTE="/videos/new")
        except Exception:
            db.session.rollback()
            flash("ERROR")
            return render_template("add_video.html", FORM=form, FROM_ROUTE="/videos/new")
    else:
        return render_template("add_video.html", FORM=form, FROM_ROUTE="/videos/new")

@app.route("/videos/<int:id>/edit", methods=["GET", "POST"])
def edit_video(id):
    """Edit video"""
    if not session.get("username"):
        flash("You must be logged in")
        return redirect("/")

    video = None
    try:
        video = Video.query.get(id)
        if video is None:
            raise Exception("None Exception")
        if video.user_id != session.get("user_id"):
            raise Exception("Invalid User")
    except Exception:
        flash("Edit Video Error")
        return redirect("/")

    form = EditVideoForm(obj=video)
    if form.validate_on_submit():
        try:
            form.populate_obj(video)
            db.session.add(video)
            db.session.commit()

            flash(f"{form.title.data} edited")
            return redirect("/")
        except IntegrityError as e:
            db.session.rollback()
            if len(e.orig.args) > 0:
                flash(f"args:[{e.orig.args}]")
            else:
                flash("ERROR")
            return render_template("edit_video.html", FORM=form, VIDEO_ID=id, FROM_ROUTE=f"/videos/{id}/edit")
        except Exception:
            db.session.rollback()
            flash("ERROR")
            return render_template("edit_video.html", FORM=form, VIDEO_ID=id, FROM_ROUTE=f"/videos/{id}/edit")
    else:
        return render_template("edit_video.html", FORM=form, VIDEO_ID=id, FROM_ROUTE=f"/videos/{id}/edit")

@app.route("/videos/<int:id>/delete", methods=["POST"])
def delete_video(id):
    """Delete video"""
    if not session.get("username"):
        return "You must be logged in"

    try:
        video = Video.query.get(id)
        if video is None:
            raise Exception("None Exception")
        if video.user_id != session.get("user_id"):
            raise Exception("Invalid User")
        
        db.session.delete(video)
        db.session.commit()
        return "OK"
    except IntegrityError as e:
        db.session.rollback()
        flash("IntegrityError")
        return "IntegrityError"
    except Exception as e:
        db.session.rollback()
        flash("Exception")
        return "Exception"

# ==================================================

# -------------------- SEARCH --------------------

# TODO: media queries

@app.route("/search", methods=["GET", "POST"])
def search():
    """Show search page"""
    if not session.get("username"):
        flash("You must be logged in")
        return redirect("/")
    if not session.get("user_id"):
        flash("You must be logged in")
        return redirect("/")

    form_log = LogInOutForm()
    form_add_playlist_button = AddPlaylistButtonForm()
    form_add_video_button = AddVideoButtonForm()
    form_edit_playlist_button = EditPlaylistButtonForm()
    form_search = SearchForm()

    playlists = Playlist.query.filter(Playlist.user_id == session["user_id"]).order_by(Playlist.name.asc()).all()
    playlist_count = len(playlists)
    videos = Video.query.filter(Video.user_id == session["user_id"]).order_by(Video.artist.asc(), Video.title.asc()).all()
    video_count = len(videos)

    user = None
    try:
        user = User.query.get(session.get("user_id"))
        if user is None:
            flash("None Exception")
            return redirect("/")
    except Exception:
        flash("Get User Error")
        return redirect("/")

    if user.search_date.date() < datetime.datetime.now().date():
        user.search_date = datetime.datetime.now().date()
        user.searches = 0

        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash("ERROR")
            return redirect("/")

    searches = MAX_SEARCHES - user.searches

    if searches < 1:
        flash("No remaining searches available today")
        return redirect("/")

    if form_search.validate_on_submit():
        keywords = form_search.keywords.data
        keywords = "+".join(keywords.strip().replace("|", "%7C").split())

        user.searches = user.searches + 1
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash("ERROR")
            return redirect("/")
        searches = MAX_SEARCHES - user.searches

        #resp = requests.get(f"https://www.googleapis.com/youtube/v3/search?key={SECRET_API_KEY}&part=snippet&fields=items(id,snippet(title,thumbnails.default.url))&maxResults=50&type=video&videoEmbeddable=true&q={keywords}")
        #json = resp.json()
        json = "{'items': [{'id': {'kind': 'youtube#video', 'videoId': 'cNJtrqb4Pl0'}, 'snippet': {'title': 'Geddy Lee Discusses The Way Rush Ended', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/cNJtrqb4Pl0/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': '04Ekje672mo'}, 'snippet': {'title': 'Rush&#39;s Geddy Lee on his Fender USA Geddy Lee Jazz Bass | Fender', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/04Ekje672mo/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'auLBLk4ibAk'}, 'snippet': {'title': 'Rush - Tom Sawyer (Official Music Video)', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/auLBLk4ibAk/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'uCr0f5S06A4'}, 'snippet': {'title': 'ASG 1993: Rush&#39;s Geddy Lee sings O Canada', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/uCr0f5S06A4/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'nEVDZl5UvN4'}, 'snippet': {'title': 'Rush - Fly By Night (Official Music Video)', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/nEVDZl5UvN4/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'ZrstPbrL1ss'}, 'snippet': {'title': 'Rush Fan Day Interview with Geddy Lee and Alex Lifeson', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/ZrstPbrL1ss/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'HGdQUMzRVxA'}, 'snippet': {'title': 'Geddy Lee ( bass Solo ) Time Machine 2011', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/HGdQUMzRVxA/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'GBVya4G8uNQ'}, 'snippet': {'title': 'The Big Interview with Dan Rather: Geddy Lee of Rush - Sneak Peek | AXS TV', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/GBVya4G8uNQ/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'Q0UEngM9AXI'}, 'snippet': {'title': 'Rock Icons Rushs Geddy Lee Documentary', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/Q0UEngM9AXI/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': '6JiBs6Dkiwo'}, 'snippet': {'title': 'The Only Band That Geddy Lee of Rush Ever Stood In Line For', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/6JiBs6Dkiwo/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': '7kveiFvr0Uk'}, 'snippet': {'title': 'Rush - Tom Sawyer - Geddy Lee voice change', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/7kveiFvr0Uk/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'jIMmdOZlmrU'}, 'snippet': {'title': 'Rush&#39;s Geddy Lee on his obsession with the history of the bass guitar', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/jIMmdOZlmrU/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'gu7zKwerKCM'}, 'snippet': {'title': 'That Metal Show | Rush&#39;s Geddy Lee: Behind the Scenes | VH1 Classic', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/gu7zKwerKCM/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'hPxwSF4CGyo'}, 'snippet': {'title': 'Geddy Lee Tells His Family&#39;s Holocaust Story (Full Interview)', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/hPxwSF4CGyo/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'sWVs5iSYTdM'}, 'snippet': {'title': 'Geddy Lee on his ‘Book of Bass’ and why Rush won’t tour again', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/sWVs5iSYTdM/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'L82ARErk5LQ'}, 'snippet': {'title': 'Geddy Lee from Rush visits Norman&#39;s Rare Guitars', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/L82ARErk5LQ/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'ZBtuCyjqn8E'}, 'snippet': {'title': 'Rush: The Final Year of Neil Peart&#39;s Life Revealed &amp; Last Public Photo', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/ZBtuCyjqn8E/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': '5NXdxQDkTwU'}, 'snippet': {'title': 'Geddy Lee plays Jam or Not a Jam', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/5NXdxQDkTwU/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'OeKzKf8rX4E'}, 'snippet': {'title': 'Geddy Lee before Rush', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/OeKzKf8rX4E/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 't1-NsnlPc54'}, 'snippet': {'title': 'Yes Roundabout with Geddy Lee on Rock &amp; Roll Hall of Fame 2017', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/t1-NsnlPc54/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': '631yLIjqACM'}, 'snippet': {'title': 'Geddy Lee on his ‘Book of Bass’ and why Rush won’t tour again', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/631yLIjqACM/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': '-SZbGQ-pTZY'}, 'snippet': {'title': 'Geddy Lee Explains His Right-Hand Picking Technique | Fender', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/-SZbGQ-pTZY/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'GFze-Oj2UdA'}, 'snippet': {'title': 'Rush Answers Your Twitter and Facebook Questions', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/GFze-Oj2UdA/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'SouCSF45K48'}, 'snippet': {'title': 'Rush - YYZ (Live HD)', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/SouCSF45K48/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'dMSFqXGZ5TQ'}, 'snippet': {'title': 'Rush - Time Stand Still (Official Music Video)', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/dMSFqXGZ5TQ/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'kOAPd1kfPNk'}, 'snippet': {'title': 'Rush - Limelight', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/kOAPd1kfPNk/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': '34wk_onk50E'}, 'snippet': {'title': 'Geddy Lee from Rush Interview at Abbey Road Studios', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/34wk_onk50E/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': '2rdDbqQyJMA'}, 'snippet': {'title': 'Rush&#39;s Alex Lifeson Hasn&#39;t Felt Inspired Since Neil Peart&#39;s Death', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/2rdDbqQyJMA/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'LhfGASMhKeQ'}, 'snippet': {'title': 'GEDDY LEE - RUSH - WINTER CELEBRITY ADVICE', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/LhfGASMhKeQ/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'aSEO-aJVq78'}, 'snippet': {'title': 'That Metal Show | Rush&#39;s Geddy Lee On Being A Baseball Fan | VH1 Classic', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/aSEO-aJVq78/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'SEuOoMprDqg'}, 'snippet': {'title': 'Rush - Xanadu (Official Music Video)', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/SEuOoMprDqg/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'jpAmK111ACk'}, 'snippet': {'title': 'Geddy Lee Bass Rig - RUSH - Know Your Bass Player', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/jpAmK111ACk/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'JnC88xBPkkc'}, 'snippet': {'title': 'Rush - The Trees (Official Music Video)', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/JnC88xBPkkc/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'ejtHdjd3BGI'}, 'snippet': {'title': 'Rush - R40 Tour - Geddy Lee Webisode Part 2', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/ejtHdjd3BGI/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'Af2-WQE_j4c'}, 'snippet': {'title': 'RUSH interview - Geddy Lee and Alex Lifeson - Brazil - november 2002', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/Af2-WQE_j4c/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'dptj4dMuS1w'}, 'snippet': {'title': 'Geddy Lee Amazing Bass Solo', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/dptj4dMuS1w/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'ykGIq_fBa3U'}, 'snippet': {'title': 'Rush | The Legend of &quot;The Bag&quot; | Time Stand Still', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/ykGIq_fBa3U/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'OQDDzq792Qw'}, 'snippet': {'title': 'RUSH - &quot;Tom Sawyer&quot; (live 1988)', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/OQDDzq792Qw/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'eV-5iNu6Sd8'}, 'snippet': {'title': 'Rush - A Farewell To Kings (Official Music Video)', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/eV-5iNu6Sd8/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'KzrOt-ZxpVc'}, 'snippet': {'title': 'Você quer o Rush sem Neil Peart? | Papo Reto | Alta Fidelidade', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/KzrOt-ZxpVc/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'dqYiTTD1IXg'}, 'snippet': {'title': 'Northern Lights - Rush - Geddy Lee', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/dqYiTTD1IXg/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'yrZJebJFou8'}, 'snippet': {'title': 'Rush &quot;The Big Money&quot;  Geddy Lee Bass Part', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/yrZJebJFou8/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'yz5UBnk-JOg'}, 'snippet': {'title': 'Geddy Lee on being the a Child of a Holocaust Survivor | SiriusXM Town Hall with Rush', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/yz5UBnk-JOg/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': '7A-48kvH02k'}, 'snippet': {'title': 'Alex Lifeson and Geddy Lee both post to Social Media - first time since Neil Peart&#39;s passing', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/7A-48kvH02k/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': '7qa7p6gFIGw'}, 'snippet': {'title': 'That Metal Show | Rush&#39;s Geddy Lee Ranks Best Of Rush Albums | VH1 Classic', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/7qa7p6gFIGw/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'fZvVBZZDHRE'}, 'snippet': {'title': 'The Singing Style of Geddy Lee - RUSH... Light, Bright,  Mixed Voice. (PS Thank You Neil Peart)', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/fZvVBZZDHRE/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'U6qyhiVPzCg'}, 'snippet': {'title': 'Geddy Lee signs autographs for RUSH fans on Hollywood Walk of Fame', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/U6qyhiVPzCg/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'omumqjSurAM'}, 'snippet': {'title': 'Rush Snakes &amp; Arrows Tour - Geddy Lee - Tuning Room Interview', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/omumqjSurAM/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'ONFuKLgP-70'}, 'snippet': {'title': 'Rush Geddy Lee Tom Sawyer Bass Lesson', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/ONFuKLgP-70/default.jpg'}}}}, {'id': {'kind': 'youtube#video', 'videoId': 'VL_7pVb2lI0'}, 'snippet': {'title': 'Geddy Lee on Religion', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/VL_7pVb2lI0/default.jpg'}}}}]}"

        return render_template("/search.html", FORM_LOG=form_log, USER_ID=session.get("user_id"), VIDEO=None, VIDEOS=videos, MAX_VIDEOS=MAX_VIDEOS, VIDEO_COUNT=video_count, PLAYLISTS=playlists, MAX_PLAYLISTS=MAX_PLAYLISTS, PLAYLIST_COUNT=playlist_count, SEARCHES=searches, FORM_ADD_PLAYLIST_BUTTON=form_add_playlist_button, FORM_ADD_VIDEO_BUTTON=form_add_video_button, FORM_EDIT_PLAYLIST_BUTTON=form_edit_playlist_button, FORM_SEARCH=form_search, FROM_ROUTE="/search")
    else:
        return render_template("/search.html", FORM_LOG=form_log, USER_ID=session.get("user_id"), VIDEO=None, VIDEOS=videos, MAX_VIDEOS=MAX_VIDEOS, VIDEO_COUNT=video_count, PLAYLISTS=playlists, MAX_PLAYLISTS=MAX_PLAYLISTS, PLAYLIST_COUNT=playlist_count, SEARCHES=searches, FORM_ADD_PLAYLIST_BUTTON=form_add_playlist_button, FORM_ADD_VIDEO_BUTTON=form_add_video_button, FORM_EDIT_PLAYLIST_BUTTON=form_edit_playlist_button, FORM_SEARCH=form_search, FROM_ROUTE="/search")

# ==================================================
