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
    reg_username = StringField("Username", validators=[InputRequired()])
    reg_password = PasswordField("Password", validators=[InputRequired()])
    reg_confirm = PasswordField("Confirm", validators=[InputRequired()])
    reg_email = StringField("Email", validators=[InputRequired()])
    reg_pacode = StringField("Public Access Code")

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
