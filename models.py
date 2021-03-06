from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)

# -------------------- User --------------------

class User(db.Model):
    __tablename__ = "users"

    def __repr__(self):
        return f"<Username:{self.username} Email:{self.email} PACode:{self.public_access_code}>"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    public_access_code = db.Column(db.String(50), unique=True)
    searches = db.Column(db.Integer, nullable=False)
    search_date = db.Column(db.DateTime, nullable=False)
    keywords = db.Column(db.String(50), nullable=False)
    json = db.Column(db.Text, nullable=False)

    @classmethod
    def register(cls, username, pwd, email, pacode, searches, search_date):
        """Register user w/hashed password & return user."""
        hashed = bcrypt.generate_password_hash(pwd) # (pwd, work_factor)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")
        # return instance of user w/username and hashed pwd
        return cls(username=username, password=hashed_utf8, email=email, public_access_code=pacode, searches=searches, search_date=search_date, keywords="", json="")

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.
        Return user if valid; else return False.
        """
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, pwd):
            return user
        else:
            return False

# ==================================================

# -------------------- Video --------------------

class Video(db.Model):
    __tablename__ = "videos"

    def __repr__(self):
        return f"<Artist:{self.artist} Title:{self.title} Video:{self.video_id} User:{self.user_id} ID:{self.id}>"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    title = db.Column(db.String(50), nullable=False)
    artist = db.Column(db.String(50), nullable=False)
    video_id = db.Column(db.String, nullable=False)

    db.UniqueConstraint(user_id, title, artist)
#args:[('duplicate key value violates unique constraint "videos_user_id_title_artist_key"\nDETAIL: Key (user_id, title, artist)=(1, b, c) already exists.\n',)]

    playlists = db.relationship("Playlist", secondary="playlists_videos")

# ==================================================

# -------------------- Playlist --------------------

class Playlist(db.Model):
    __tablename__ = "playlists"

    def __repr__(self):
        return f"<Playlist:{self.name}  ID:{self.id}>"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    name = db.Column(db.String(50), nullable=False)

    db.UniqueConstraint(user_id, name)

    videos = db.relationship("Video", secondary="playlists_videos", order_by="Video.artist, Video.title")

# ==================================================

# -------------------- Playlists_Videos --------------------

class Playlists_Videos(db.Model):
    __tablename__ = "playlists_videos"

    def __repr__(self):
        return f"<Playlist:{self.playlist_id}  Video:{self.video_id}>"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey("playlists.id"))
    video_id = db.Column(db.Integer, db.ForeignKey("videos.id"))

    playlists = db.relationship(Playlist, backref=db.backref("playlists_videos", cascade="all, delete-orphan"))
    videos = db.relationship(Video, backref=db.backref("playlists_videos", cascade="all, delete-orphan"))

# ==================================================
