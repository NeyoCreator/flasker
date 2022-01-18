#Imports
from enum import unique
from flask import Flask,render_template,flash,request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField, BooleanField, ValidationError
from wtforms import validators
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea


#Flask Intsance
app = Flask(__name__)

#Add to database SQLITE
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

#MYSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:BOSS97kills!@localhost/new_users'

#Secrete Key!
app.config['SECRET_KEY'] = 'any secret string'

#Initilise  Database
db = SQLAlchemy(app)
migrate=Migrate(app,db)

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

#Blog Model
class Posts(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(255))
    content=db.Column(db.Text)
    author=db.Column(db.String(255))
    date_posted=db.Column(db.DateTime, default=datetime.utcnow)
    slug=db.Column(db.String(255))

#User Form Class
class UserForm(FlaskForm):
    name=StringField("Name",validators=[DataRequired()])
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
    author=StringField("Author",validators=[DataRequired()])
    slug=StringField("SlugFied",validators=[DataRequired()])
    submit=SubmitField("Submit")

#Post Page
@app.route('/posts')
def posts():
    #Grab Posts
    posts=Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html",posts=posts)

#Add Post
@app.route('/add-post',methods=['GET','POST'])
def add_post():
    form=PostForm()
    if form.validate_on_submit():
        post=Posts(title=form.title.data,content=form.content.data,author=form.author.data,slug=form.slug.data)
        form.title.data=''
        form.content.data=''
        form.author.data=''
        form.slug.data=''
        #Add Database
        db.session.add(post)
        db.session.commit()
        flash("Data Added successfully!")
        
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
        flash("There was a problem deleting user")
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
    return render_template("index.html",first_name =first_name,stuff =stuff,favourite_pizza = favourite_pizza)

#Add User
@app.route('/user/add',methods=['GET','POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()  
        if user is None:
            #Hash Password
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

@app.route('/user/<name>')
def user(name):
    return render_template('user.html',name =name )

#Bank Statement
@app.route('/bank')
def bank():
    return render_template('bank_statement.html')

#Invalid URL 
@app.errorhandler(404) 
def page_not_found(e):
    return render_template("404.html"),404


#Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"),500

#Namer Page
@app.route('/name',methods=['GET','POST'])
def name():
    name = None
    form = NamerForm()

    #Validate Form
    if form.validate_on_submit():
        name = form.name.data
        flash(form.name.data +" your name has been submited Succefully!")
        form.name.data= ''
 
    return render_template('name.html',
    name = name,
    form = form)

    


