#Imports
from crypt import methods
from email import contentmanager
from email.policy import default
from enum import unique
from tkinter import Widget
from turtle import title
from flask import Flask,render_template,flash,request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField, BooleanField, ValidationError
from wtforms import validators
from  wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date   
from wtforms.widgets import TextArea


#Flask Intsance
app = Flask(__name__)

#Add to database SQLITE
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'\

#MySql Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:BOSS97kills!@localhost/new_users'

#Secrete Key
app.config['SECRET_KEY'] = 'any secret string'

#Initilise Database
db = SQLAlchemy(app)
migrate=Migrate(app,db)

#JSON
@app.route('/date')
def get_current_date():
    user_info = {"name":"tabiso","rooms":2,"location":"mamelodi"}
    return user_info

#Blog Post Model
class Post(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(255))
    content=db.Column(db.Text)
    author=db.Column(db.String(255))
    date_posted=db.Column(db.DateTime,default=datetime.utcnow)
    slug=db.Column(db.String(255))

#User Model
class Users(db.Model):
    id =  db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200), nullable = False)
    email = db.Column(db.String(120), nullable = False, unique=True)
    favourite_color=db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default= datetime.utcnow)
   
    #Password
    password_hash=db.Column(db.String(128))
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')
    
    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def __rep__(self):
        return '<Name %r>' % self.name

#Post Form
class PostForm(FlaskForm):
    title=StringField("Title",validators=[DataRequired()])
    content=StringField("Content",validators=[DataRequired()],widget=TextArea())
    author=StringField("Author",validators=[DataRequired()])
    slug=StringField("Slug",validators=[DataRequired()])
    submit=StringField("Submit",validators=[DataRequired()])

#User Form
class UserForm(FlaskForm):
    name=StringField("Name",validators=[DataRequired()])
    email=StringField("E-mail",validators=[DataRequired()])
    favourite_color=StringField("Favourite color")
    password_hash=PasswordField("Password", validators=[DataRequired(),EqualTo("password_hash2",message="Passwords Must Match!")])
    password_hash2=PasswordField("Confirm Paword",validators=[DataRequired()])
    submit = SubmitField("submit")

#Password Form
class PasswordForm(FlaskForm):
    email=StringField("Whats your email?",validators=[DataRequired()])
    password_hash=PasswordField("Whats your password?",validators=[DataRequired()])
    submit=SubmitField("Submit")
    
#Namer Form
class NamerForm(FlaskForm):
    name=StringField("Whats your name",validators=[DataRequired()])
    submit=SubmitField("Submit")

#Post Page
@app.route('/add-post',methods=["GET","POST"])
def add_post():
    form=PostForm()
    if form.validate_on_submit():
        post=Post(title=form.title.data,content=form.content.data,slug=form.slug.data)
        #Clear Form
        form.title.data=""
        form.content.data=""
        form.author.data=""
        form.slug.data=""

        #Add Post Database
        db.session.add(post)
        db.session.commmit()
        flash("Blog post submitted successfully")
    return render_template("add_post.html",form=form)


#Delete Database Record
@app.route('/delete/<int:id>')
def delete(id):
    form=None
    name=UserForm()
    user_to_delete=Users.query.get_or_404(id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("Deleted Successfully")
        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html",form=form,name=name,our_users= our_users)
    except:
        flask("There was a problem deleting user")
        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html",form=form,name=name,our_users= our_users)
        
#Update Database Record
@app.route('/update/<int:id>', methods=['POST','GET'])
def update(id):
    form=UserForm()
    name_to_update=Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name=request.form['name']
        name_to_update.email=request.form['email']
        name_to_update.favourite_color=request.form['favourite_color']
        try :
            db.session.commit()
            flash("User updated succesfully")
            return render_template('update.html',form=form,name_to_update=name_to_update)
        except:
            flash("Error!There has been a problem")
            return render_template('update.html',form=form,name_to_update=name_to_update,id=id)
    else:
        return render_template('update.html',form=form,name_to_update=name_to_update,id=id)
        
#Home Page
@app.route('/')
def index():
    first_name = 'Neo'
    stuff = 'This is <strong>Bold</strong> Text'

    favourite_pizza= ["peperonni", "cheese","mushroom",41]
    return render_template("index.html", 
    first_name =first_name,
    stuff =stuff,
    favourite_pizza = favourite_pizza
    )

#Add User
@app.route('/user/add',methods=['GET','POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()  
        if user is None:
            #Hash the password!
            hashed_pw=generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name=form.name.data, email=form.email.data,favourite_color=form.favourite_color.data,password_hash=hashed_pw) 
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data=''
        form.email.data=''
        form.favourite_color.data=''
        form.password_hash.data=''
        flash("User added successfully")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html",form=form,name=name,our_users= our_users)

#User
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name =name )

#Bank Satement
@app.route('/bank')
def bank():
    return render_template('bank_statement.html')

#Invalid URL 
@app.errorhandler(404) 
def page_not_found(e):
    return render_template("404.html"),404

#Internal Servererror
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"),500

#Password Test Page
@app.route('/test_pw',methods=['GET','POST'])
def test_pw():
    email=None
    password=None
    pw_to_check=None
    passed=None
    form = PasswordForm()

    #Validate Form
    if form.validate_on_submit():
        email=form.email.data
        password=form.password_hash.data
        form.email.data= ''
        form.password_hash.data=''

        #Look Up User
        pw_to_check= Users.query.filter_by(email=email).first()

        #Check Hashed Password
        passed = check_password_hash(pw_to_check.password_hash,password)

    return render_template('test_pw.html',email=email,password=password,pw_to_check=pw_to_check,passed=passed,form=form)

#Name Page
@app.route('/name',methods=['GET','POST'])
def name():
    name = None
    form = NamerForm()

    #Validate Form
    if form.validate_on_submit():
        name = form.name.data
        flash(form.name.data +" your name has been submited Succefully!")
        form.name.data= ''
    return render_template('name.html',name = name,form = form)

    


