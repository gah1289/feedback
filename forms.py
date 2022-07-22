from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import InputRequired

class RegisterForm(FlaskForm):
    '''Generate register form to input new user information'''
    username= StringField("Username", validators=[InputRequired()])
    password= PasswordField("Password", validators=[InputRequired()])
    email= EmailField("Email", validators=[InputRequired()])
    first_name=StringField("First Name", validators=[InputRequired()])
    last_name=StringField("Last Name", validators=[InputRequired()])

class LoginForm(FlaskForm):
    '''Generate Login Form requiring username and password'''

    username= StringField("Username", validators=[InputRequired()])
    password= PasswordField("Password", validators=[InputRequired()])

class FeedbackForm(FlaskForm):
    '''Add a new piece of feedback'''
    title=StringField("Title", validators=[InputRequired()])
    content=StringField("Content", validators=[InputRequired()])

