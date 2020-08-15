from flask import Flask, request, render_template, redirect, session, flash, make_response
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Video, Playlist, Playlists_Videos
from forms import AddPlaylistForm, AddPlaylistButtonForm, AddVideoForm, AddVideoButtonForm, EditUserForm, EditPlaylistForm, EditPlaylistButtonForm, EditVideoForm, EditVideoButtonForm, LogInOutForm, RegisterForm
from wtforms import BooleanField

app = Flask(__name__)
app.config["SECRET_KEY"] = "Don't look at me."
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///JukeBoxDB"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
#app.config["TESTING"] = True
#app.config["DEBUG_TB_HOSTS"] = ["dont-show-debug-toolbar"]
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
debug = DebugToolbarExtension(app)

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
    videos = None
    if session.get("user_id"):
        playlists = Playlist.query.filter(Playlist.user_id == session["user_id"]).order_by(Playlist.name.asc()).all()
        videos = Video.query.filter(Video.user_id == session["user_id"]).order_by(Video.artist.asc(), Video.title.asc()).all()

    return render_template("/extends/home.html", USER_ID=session.get("user_id"), PLAYLISTS=playlists, VIDEOS=videos, FORM_LOG=form_log, FORM_ADD_PLAYLIST_BUTTON=form_add_playlist_button, FORM_ADD_VIDEO_BUTTON=form_add_video_button, FORM_EDIT_PLAYLIST_BUTTON=form_edit_playlist_button, FORM_EDIT_VIDEO_BUTTON=form_edit_video_button, FROM_ROUTE="/")

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

        user = User.register(name, pwd, email, pacode)
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

# -------------------- TEMPORARY --------------------

@app.route("/private")
def private():
    """Private page."""
    if not session.get("username"):
        flash("You must be logged in")
        return redirect("/")
    
    form_log = LogInOutForm()
    form_add_video_button = AddVideoButtonForm()
    form_edit_video_button = EditVideoButtonForm()
    return render_template("/extends/private.html", FORM_LOG=form_log, FORM_ADD_VIDEO_BUTTON=form_add_video_button, FORM_EDIT_VIDEO_BUTTON=form_edit_video_button, FROM_ROUTE="/private")

@app.route("/secret")
def secret():
    """Example page."""
    form_log = LogInOutForm()
    form_add_video_button = AddVideoButtonForm()
    form_edit_video_button = EditVideoButtonForm()
    return render_template("/extends/secret.html", FORM_LOG=form_log, FORM_ADD_VIDEO_BUTTON=form_add_video_button, FORM_EDIT_VIDEO_BUTTON=form_edit_video_button, FROM_ROUTE="/secret")

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

@app.route("/playlists/new", methods=["GET", "POST"])
def add_playlist():
    """Add playlist"""
    if not session.get("username"):
        flash("You must be logged in")
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

            flash(f"{form.name.data} added")

            for key, value in form.data.items():
                if not key.isdigit():
                    continue
                if not value:
                    continue
                join = Playlists_Videos(
                    playlist_id=playlist.id,
                    video_id=int(key))
                db.session.add(join)
            db.session.commit()

            return redirect("/")
        except IntegrityError as e:
            db.session.rollback()
            if len(e.orig.args) > 0:
                flash(f"args:[{e.orig.args}]")
            else:
                flash("ERROR")
            return render_template("add_playlist.html", VIDEOS=videos, FORM=form, FROM_ROUTE="/playlists/new")
        except Exception:
            db.session.rollback()
            flash("ERROR")
            return render_template("add_playlist.html", VIDEOS=videos, FORM=form, FROM_ROUTE="/playlists/new")
    else:
        return render_template("add_playlist.html", VIDEOS=videos, FORM=form, FROM_ROUTE="/playlists/new")

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
    print(f"Videos in Playlist:{video_IDs}")
    print(f"Videos in Playlist:{playlist.videos}")

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
            print("---=== edit_playlist ===---")
            playlist.name = form.name.data
            db.session.commit()

            flash(f"{form.name.data} edited")

            print(f"In Playlist:{video_IDs}")

            print(f"Videos in Playlist:{video_IDs}")
            print(f"Videos in Playlist:{playlist.videos}")
            for key, value in form.data.items():
                if not key.isdigit():
                    print(f"key:{key}")
                    continue
                if not value:
                    print(f"value:{value}")
                    continue

                video_id = int(key)
                print(f"checked:{key}")
                if video_id in video_IDs:
                    video_IDs.remove(video_id)
                    print(f"already:{video_id}")
                    continue

                print(f"add:{key}")
                join = Playlists_Videos(
                    playlist_id=playlist.id,
                    video_id=video_id)
                print(join)
                db.session.add(join)
                db.session.commit()
                video_IDs.remove(video_id)

            print(f"Delete from Playlist:{video_IDs}")

            for video_id in video_IDs.copy():
                p_v = Playlists_Videos.query.filter(Playlists_Videos.playlist_id == playlist.id, Playlists_Videos.video_id == video_id).first()
                if p_v is not None:
                    print(p_v)
                    print(f"Videos in Playlist:{playlist.videos}")
                    db.session.delete(p_v)
                    db.session.commit()
                    print("After Delete")
                video_IDs.remove(video_id)

            print(f"Set final:{video_IDs}")

            db.session.commit()

            print("***** redirect *****")
            return redirect("/")
        except IntegrityError as e:
            db.session.rollback()
            if len(e.orig.args) > 0:
                flash(f"args:[{e.orig.args}]")
            else:
                flash("ERROR")
            print("***** IntegrityError *****")
            print(e)
            return render_template("edit_playlist.html", VIDEOS=videos, FORM=form, PLAYLIST_ID=id, FROM_ROUTE=f"/playlist/{id}/edit")
        except Exception as e:
            db.session.rollback()
            flash("ERROR")
            print("***** Exception *****")
            print(repr(e))
            print("********************")
            return render_template("edit_playlist.html", VIDEOS=videos, FORM=form, PLAYLIST_ID=id, FROM_ROUTE=f"/playlist/{id}/edit")
    else:
        return render_template("edit_playlist.html", VIDEOS=videos, FORM=form, PLAYLIST_ID=id, FROM_ROUTE=f"/playlists/{id}/edit")

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

#@app.route("/videos")
#def videos_list():
#    """List of videos"""
#    return render_template("videos.html", TITLE="Videos", VIDEO=Video.query.order_by(Video.ast_name.asc(),Video.first_name.asc()).all())

@app.route("/videos/new", methods=["GET", "POST"])
def add_video():
    """Add video"""
    if not session.get("username"):
        flash("You must be logged in")
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

#@app.route("/videos/<int:video_id>")
#def watch_video(video_id):
#    """Watch video"""
#    video = Video.query.get(id)
#    posts = Post.query.filter(Post.video_id==id).all()
#    return render_template("video.html", TITLE=video.full_name, ##VIDEO=video, POSTS=posts)
#    return

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
