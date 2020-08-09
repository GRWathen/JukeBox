from flask import Flask, request, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Video, Playlist, Playlists_Videos
from forms import AddVideoForm, AddVideoButtonForm, LogInOutForm, RegisterForm

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
    form_add_video_button = AddVideoButtonForm()

    print("***** HOME *****")
    videos = None
    if session.get("user_id"):
        print(f"ID:{session['user_id']}")
        videos = Video.query.filter(Video.user_id == session["user_id"]).order_by(Video.artist.asc(), Video.title.asc()).all()
        print("---=== VIDEOS ===---")
        print(videos)
        print("====================")

    return render_template("/extends/home.html", VIDEOS=videos, FORM_LOG=form_log, FORM_ADD_VIDEO_BUTTON=form_add_video_button, FROM_ROUTE="/")

# ---------- REGISTER / LOGIN / LOGOUT ----------

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user: produce form & handle form submission."""
    form_log = LogInOutForm()
    form_register = RegisterForm()

    if form_register.validate_on_submit():
        error = False

        name = form_register.reg_username.data
        if name is None or len(name) == 0:
            error = True
            form_register.reg_username.errors.append("Username may not be blank")
        
        pwd = form_register.reg_password.data
        if pwd is None or len(pwd) == 0:
            error = True
            form_register.reg_password.errors.append("Password may not be blank")
        
        confirm = form_register.reg_confirm.data
        if confirm != pwd:
            error = True
            form_register.reg_confirm.errors.append("Confirm Password and Password must be the same")
        
        # TODO: Validate email
        email = form_register.reg_email.data
        if email is None or len(email) == 0:
            error = True
            form_register.reg_email.errors.append("Email may not be blank")
        
        pacode = form_register.reg_pacode.data
        if pacode is None or len(pacode) == 0:
            pacode = None
        
        if error:
            return render_template("register.html", FORM_LOG=form_log, FORM_REGISTER=form_register, FROM_ROUTE="/register")

        user = User.register(name, pwd, email, pacode)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError as e:
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
    return render_template("/extends/private.html", FORM_LOG=form_log, FORM_ADD_VIDEO_BUTTON=form_add_video_button, FROM_ROUTE="/private")

@app.route("/secret")
def secret():
    """Example page."""
    form_log = LogInOutForm()
    form_add_video_button = AddVideoButtonForm()
    return render_template("/extends/secret.html", FORM_LOG=form_log, FORM_ADD_VIDEO_BUTTON=form_add_video_button, FROM_ROUTE="/secret")

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
            if len(e.orig.args) > 0:
                flash(f"args:[{e.orig.args}]")
            else:
                flash("ERROR 0")
            return render_template("add_video.html", FORM=form, FROM_ROUTE="/videos/new")
    else:
        return render_template("add_video.html", FORM=form, FROM_ROUTE="/videos/new")

#@app.route("/videos/<int:id>")
#def video_detail(id):
#    """Video Detail"""
#    video = Video.query.get(id)
#    posts = Post.query.filter(Post.video_id==id).all()
#    return render_template("video.html", TITLE=video.full_name, ##VIDEO=video, POSTS=posts)

#@app.route("/videos/<int:id>/edit")
#def edit_video(id):
#    """Edit video"""
#    video = User.query.get(id)
#    return render_template("edit_video.html", TITLE="Edit video", ##VIDEO=video)

#@app.route("/videos/<int:id>/edit", methods=["POST"])
#def edit_video_post(id):
#    """Edit video - POST"""
#    video = User.query.get(id)
#    video.first_name = request.form["first_name"]
#    video.last_name = request.form["last_name"]
#    video.image_url = request.form["image_url"]
#    db.session.add(video)
#    db.session.commit()
#    return redirect("/videos")

#@app.route("/videos/<int:id>/delete", methods=["POST"])
#def delete_video(id):
#    """Delete User"""
#    video = User.query.get(id)
#    for post in video.posts:
#        video.posts.remove(post)
#        db.session.delete(post)
#    db.session.delete(User.query.get(id))
#    db.session.commit()
#    return redirect("/videos")

# ==================================================
