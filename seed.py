#createdb db

from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User

app = Flask(__name__)
app.config["SECRET_KEY"] = "Don't look at me."
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///JukeBoxDB"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
#app.config["TESTING"] = True
#app.config["DEBUG_TB_HOSTS"] = ["dont-show-debug-toolbar"]
#app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
debug = DebugToolbarExtension(app)

connect_db(app)
def seed():
    print("SEED BEGIN")
    db.drop_all()
    db.create_all()
    User.query.delete()

    #user1 = User(username="grw", password="password")
    #user2 = User(username="da", password="secret")

    #db.session.add(user1)
    #db.session.add(user2)

    db.session.commit()
    print("SEED END")
#seed()

@app.route("/favicon.ico")
def fav_icon():
    """Favorite Icon"""
    return ""

@app.route("/")
def homepage():
    """Show homepage"""
    return render_template("seed.html")
