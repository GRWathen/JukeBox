from flask import Flask, request, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Video, Playlist, Playlists_Videos
from forms import LogInOutForm, RegisterForm

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
    return render_template("home.html", form_log=form_log, from_route="/")

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
            error = True
            form_register.reg_pacode.errors.append("Public Access Code may not be blank")
        
        if error:
            return render_template("register.html", form_log=form_log, form_register=form_register, from_route="/register")

        user = User.register(name, pwd, email, pacode)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            flash("Invalid Username and/or Password")
            form_register.username.errors.append("Invalid name/password")
            return render_template("register.html", form_log=form_log, form_register=form_register, from_route="/register")

        session["username"] = user.username
        # on successful login, redirect to secret page
        flash("Logged In")
        return redirect("/secret")
    else:
        return render_template("register.html", form_log=form_log, form_register=form_register, from_route="/register")

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
            session["username"] = user.username  # keep logged in
            flash("Logged In")
            return redirect("/secret")
        else:
            flash("Invalid Username and/or Password")

    return redirect(from_route)

@app.route("/logout", methods=["POST"]) # TODO: should be POST - empty form to submit
def logout():
    """Logs user out and redirects to homepage."""
    if session.get("username"):
        session.pop("username")
        flash("Logged Out")
    return redirect("/")

@app.route("/secret")
def secret():
    """Example page."""
    form_log = LogInOutForm()
    return render_template("secret.html", form_log=form_log, from_route="/secret")
