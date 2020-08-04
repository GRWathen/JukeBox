from flask import Flask, request, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Video, Playlist, Playlists_Videos
from forms import LogInOutForm, RegisterForm #, LoginForm, LogoutForm

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

@app.route("/")
def homepage():
    """Show homepage"""
    form_log = LogInOutForm()
    return render_template("home.html", form_log=form_log, from_url="home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user: produce form & handle form submission."""
    form_log = LogInOutForm()
    form_register = RegisterForm()
    if form_register.validate_on_submit():
        name = form_register.username.data
        pwd = form_register.password.data

        user = User.register(name, pwd)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            form_register.username.errors.append("Invalid name/password")
            return render_template("register.html", form_log=form_log, form_register=form_register, from_url="register.html")

        session["user_id"] = user.id
        # on successful login, redirect to secret page
        flash("Logged In")
        return redirect("/secret")
    else:
        return render_template("register.html", form_log=form_log, form_register=form_register, from_url="register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Produce login form or handle login."""
    form_log = LogInOutForm()

    print("---=== Log In ===---")
    print(request.form)
    print(request.form.get("username"))
    print(request.form.get("password"))
    print(request.form.get("from_url"))
    print("====================")
    from_url = request.form.get("from_url")
    if request.form.get("username") is None:
        flash("username")
        return render_template(from_url, form_log=form_log)
    if request.form.get("password") is None:
        flash("password")
        return render_template(from_url, form_log=form_log)
    if form_log.validate_on_submit():
        name = form_log.username.data
        pwd = form_log.password.data

        # authenticate will return a user or False
        user = User.authenticate(name, pwd)
        if user:
            session["user_id"] = user.id  # keep logged in
            flash("Logged In")
            return redirect("/secret")
        else:
            form_log.username.errors = ["Invalid name/password"]

    return render_template(from_url, form_log=form_log)

@app.route("/logout") # TODO: should be POST - empty form to submit
def logout():
    """Logs user out and redirects to homepage."""
    if session.get("user_id"):
        session.pop("user_id")
        flash("Logged Out")
    return redirect("/")

@app.route("/secret")
def secret():
    """Example page."""
    form_log = LogInOutForm()
    return render_template("secret.html", form_log=form_log, from_url="secret.html")
