#createdb db

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Video, Playlist, Playlists_Videos
#from secrets import SECRET_KEY # TODO: secrets

import os

app = Flask(__name__)
# TODO: SECRET_KEY
#app.config["SECRET_KEY"] = SECRET_KEY # localhost
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
# TODO: SQLALCHEMY_DATABASE_URI
#app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///JukeBoxDB"
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
#app.config["TESTING"] = True
#app.config["DEBUG_TB_HOSTS"] = ["dont-show-debug-toolbar"]
#app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
debug = DebugToolbarExtension(app)

connect_db(app)

print("SEED BEGIN")
db.drop_all()
db.session.commit()

db.create_all()
Playlists_Videos.query.delete()
Playlist.query.delete()
Video.query.delete()
User.query.delete()

#user1 = User(username="grw", password="password")
#user2 = User(username="da", password="secret")

#db.session.add(user1)
#db.session.add(user2)

db.session.commit()
print("SEED END")

@app.route("/favicon.ico")
def fav_icon():
    """Favorite Icon"""
    return ""

@app.route("/")
def homepage():
    """Show homepage"""
    return "<html><body>SEED</body></html>"

 #16 |       1 | The Camera Eye      | Rush              | atdNxWnrbNo
 #18 |       1 | Country Roads       | John Denver       | 1vrEljMfXYo
 #19 |       1 | Cool Change         | Little River Band | 9bKwRW0l-Qk
 #20 |       1 | Rocky Mountain High | John Denver       | eOB4VdlkzO4
 #21 |       1 | Sing                | The Carpenters    | iYjcNR7W-Ow
 #22 |       1 | Losing It           | Rush              | -j0AyWbAbrc
 #23 |       1 | Calypso             | John Denver       | q3EE83q6tzw
 #24 |       1 | For All We Know     | The Carpenters    | mSgIQ_4bzak
 #26 |       1 | How Much I Feel     | Ambrosia          | Ewg1LTLBGkE
