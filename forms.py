from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired

## TODO: login
#class LogInForm(FlaskForm):
#    """Form for logging in a user."""
#    log_username = StringField("Username", validators=[InputRequired()])
#    log_password = PasswordField("Password", validators=[InputRequired()])
#
## TODO: logout
#class LogOutForm(FlaskForm):
#    """Form for logging out a user."""
#
# TODO: loginout
class LogInOutForm(FlaskForm):
    """Form for logging in/out a user."""

# TODO: register
class RegisterForm(FlaskForm):
    """Form for registering a user."""
    reg_username = StringField("Username", validators=[InputRequired()])
    reg_password = PasswordField("Password", validators=[InputRequired()])
    reg_confirm = PasswordField("Confirm", validators=[InputRequired()])
    reg_email = StringField("Email", validators=[InputRequired()])
    reg_pacode = StringField("Public Access Code", validators=[InputRequired()])
