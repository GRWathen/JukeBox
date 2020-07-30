# TODO: seed
# TODO: forex component

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Video, Playlist, Playlists_Videos

app = Flask(__name__)
app.config["SECRET_KEY"] = "Don't look at me."
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///JukeBoxDB"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True # print sql to terminal
#app.config["TESTING"] = True
#app.config["DEBUG_TB_HOSTS"] = ["dont-show-debug-toolbar"]
#app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
debug = DebugToolbarExtension(app)

connect_db(app)

@app.route("/favicon.ico")
def fav_icon():
    """Favorite Icon"""
    return ""

@app.route("/")
def homepage():
    """Show homepage"""
    return return ""
