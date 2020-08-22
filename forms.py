from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Length

# -------------------- LogInOutForm --------------------

class LogInOutForm(FlaskForm):
    """Form for logging in/out a user"""

# ==================================================

# -------------------- RegisterForm --------------------

class RegisterForm(FlaskForm):
    """Form for registering a user"""
    username = StringField("Username", validators=[InputRequired(), Length(min=1, max=50)])
    password = PasswordField("Password", validators=[InputRequired()])
    confirm = PasswordField("Confirm", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Length(min=1, max=50)])
    public_access_code = StringField("Public Access Code", validators=[Length(min=0, max=50)])

# ==================================================

# -------------------- EditUserForm --------------------

class EditUserForm(FlaskForm):
    """Form for editing a user"""
    email = StringField("Email", validators=[InputRequired(), Length(max=50)])
    public_access_code = StringField("Public Access Code")

# ==================================================

# -------------------- AddPlaylistForm --------------------

class AddPlaylistForm(FlaskForm):
    """Form for adding a playlist"""
    name = StringField("Name", validators=[InputRequired(), Length(min=1, max=50)])

# ==================================================

# -------------------- AddPlaylistButtonForm --------------------

class AddPlaylistButtonForm(FlaskForm):
    """Form for add playlist button"""

# ==================================================

# -------------------- EditPlaylistForm --------------------

class EditPlaylistForm(FlaskForm):
    """Form for editing a playlist"""
    name = StringField("Name", validators=[InputRequired(), Length(min=1, max=50)])

# ==================================================

# -------------------- EditPlaylistButtonForm --------------------

class EditPlaylistButtonForm(FlaskForm):
    """Form for edit video button"""

# ==================================================

# -------------------- AddVideoForm --------------------

class AddVideoForm(FlaskForm):
    """Form for adding a video"""
    title = StringField("Title", validators=[InputRequired(), Length(min=1, max=50)])
    artist = StringField("Artist", validators=[InputRequired(), Length(min=1, max=50)])
    video_id = StringField("YouTube Video ID", validators=[InputRequired(), Length(min=1, max=50)])

# ==================================================

# -------------------- AddVideoButtonForm --------------------

class AddVideoButtonForm(FlaskForm):
    """Form for add video button"""

# ==================================================

# -------------------- EditVideoForm --------------------

class EditVideoForm(FlaskForm):
    """Form for editing a video"""
    title = StringField("Title", validators=[InputRequired(), Length(min=1, max=50)])
    artist = StringField("Artist", validators=[InputRequired(), Length(min=1, max=50)])
    video_id = StringField("YouTube Video ID", validators=[InputRequired(), Length(min=1, max=50)])

# ==================================================

# -------------------- EditVideoButtonForm --------------------

class EditVideoButtonForm(FlaskForm):
    """Form for edit video button"""

# ==================================================

# -------------------- SearchForm --------------------

class SearchForm(FlaskForm):
    """Form for seaching"""
    keywords = TextAreaField("Keywords", validators=[InputRequired(), Length(min=1, max=50)])

# ==================================================
