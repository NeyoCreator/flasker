#Imports
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField, BooleanField, ValidationError
from wtforms import StringField, SubmitField,PasswordField, BooleanField, ValidationError
from wtforms import validators
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea



#User Form Class
class UserForm(FlaskForm):
    name=StringField("Name",validators=[DataRequired()])
    username=StringField("User Name",validators=[DataRequired()])
    email=StringField("E-mail",validators=[DataRequired()])
    favourite_color=StringField("Favourite color")
    password_hash=PasswordField("Password", validators=[DataRequired(),EqualTo("password_hash2",message="Passwords Must Match!")])
    password_hash2=PasswordField("Confirm Paword",validators=[DataRequired()])
    submit = SubmitField("submit")
    
#Namer Form Class
class NamerForm(FlaskForm):
    name=StringField("Whats your name",validators=[DataRequired()])
    submit=SubmitField("Submit")

#Blog Form
class PostForm(FlaskForm):
    title=StringField("Title",validators=[DataRequired()])
    content=StringField("Content",validators=[DataRequired()],widget=TextArea())
    author=StringField("Author")
    slug=StringField("SlugFied",validators=[DataRequired()])
    submit=SubmitField("Submit")

#Login Form
class LoginForm(FlaskForm):
    username=StringField("User Name",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    submit=SubmitField("Submit")
