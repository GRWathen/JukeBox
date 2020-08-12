from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField
from wtforms.validators import InputRequired

# -------------------- LogInOutForm --------------------

class LogInOutForm(FlaskForm):
    """Form for logging in/out a user"""

# ==================================================

# -------------------- RegisterForm --------------------

class RegisterForm(FlaskForm):

    """Form for registering a user"""
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    confirm = PasswordField("Confirm", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired()])
    public_access_code = StringField("Public Access Code")

# ==================================================

# -------------------- EditUserForm --------------------

class EditUserForm(FlaskForm):

    """Form for editing a user"""
    email = StringField("Email", validators=[InputRequired()])
    public_access_code = StringField("Public Access Code")

# ==================================================

# -------------------- AddPlaylistForm --------------------

class AddPlaylistForm(FlaskForm):

    """Form for adding a playlist"""
    name = StringField("Name", validators=[InputRequired()])

# ==================================================

# -------------------- AddPlaylistButtonForm --------------------

class AddPlaylistButtonForm(FlaskForm):
    """Form for add playlist button"""

# ==================================================

# -------------------- EditPlaylistForm --------------------

class EditPlaylistForm(FlaskForm):

    """Form for editing a playlist"""
    name = StringField("Name", validators=[InputRequired()])

# ==================================================

# -------------------- EditPlaylistButtonForm --------------------

class EditPlaylistButtonForm(FlaskForm):
    """Form for edit video button"""

# ==================================================

# -------------------- AddVideoForm --------------------

class AddVideoForm(FlaskForm):

    """Form for adding a video"""
    title = StringField("Title", validators=[InputRequired()])
    artist = StringField("Artist", validators=[InputRequired()])
    video_id = StringField("Video ID")

# ==================================================

# -------------------- AddVideoButtonForm --------------------

class AddVideoButtonForm(FlaskForm):
    """Form for add video button"""

# ==================================================

# -------------------- EditVideoForm --------------------

class EditVideoForm(FlaskForm):

    """Form for editing a video"""
    title = StringField("Title", validators=[InputRequired()])
    artist = StringField("Artist", validators=[InputRequired()])
    video_id = StringField("Video ID")

# ==================================================

# -------------------- EditVideoButtonForm --------------------

class EditVideoButtonForm(FlaskForm):
    """Form for edit video button"""

# ==================================================
