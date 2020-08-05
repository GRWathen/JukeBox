from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired

class LogInOutForm(FlaskForm):
    """Form for logging in/out a user."""

class RegisterForm(FlaskForm):
    """Form for registering a user."""
    reg_username = StringField("Username", validators=[InputRequired()])
    reg_password = PasswordField("Password", validators=[InputRequired()])
    reg_confirm = PasswordField("Confirm", validators=[InputRequired()])
    reg_email = StringField("Email", validators=[InputRequired()])
    reg_pacode = StringField("Public Access Code", validators=[InputRequired()])
