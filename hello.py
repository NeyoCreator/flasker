#Imports
from enum import unique
from flask import Flask,render_template,flash,request,redirect,url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField, BooleanField, ValidationError
from wtforms import validators
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea
from flask_login import UserMixin,login_user,LoginManager,login_required,logout_user,current_user

#Flask Intsance
app = Flask(__name__)

#MYSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:BOSS97kills!@localhost/new_users'

#Secrete Key!
app.config['SECRET_KEY'] = 'any secret string'

#Initilise  Database
db = SQLAlchemy(app)
migrate=Migrate(app,db)

#Login Technicals
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'
#Set-Up
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))



#User Model
class Users(db.Model,UserMixin):
    id =  db.Column(db.Integer, primary_key = True)
    username=db.Column(db.String(20),nullable=False,unique=True)
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
    author=StringField("Author",validators=[DataRequired()])
    slug=StringField("SlugFied",validators=[DataRequired()])
    submit=SubmitField("Submit")

#Login Form
class LoginForm(FlaskForm):
    username=StringField("User Name",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    submit=SubmitField("Submit")

#Login Page
@app.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=Users.query.filter_by(username=form.username.data).first()
        if user:
            #Check Hash
            if check_password_hash(user.password_hash,form.password.data):
                login_user(user)
                flash("Logged In successfully")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong password - Try Again")
        else:
            flash("User doesn't Exist")
        
    return render_template('login.html',form=form)

#Logout Page
@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    flash("You have logged out")
    return redirect(url_for('login'))

#Dash Board
@app.route('/dashboard',methods=['GET','POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


#Delete Post
@app.route('/posts/delete/<int:id>')
def delete_post(id):
    post_to_delete=Posts.query.get_or_404(id)
    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash("Deleted Successfully")
        post=Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html',post=post)
    except:
        flash("There was an error deleting the post!")
        post=Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html',post=post)


#Edit Post
@app.route('/posts/edit/<int:id>',methods=['GET','POST'])
def edit_post(id):
    post=Posts.query.get_or_404(id)
    form=PostForm()
    if form.validate_on_submit():
        post.title=form.title.data
        post.authour=form.author.data
        post.content=form.content.data
        post.slug=form.slug.data
        #Update Database
        db.session.add(post)
        db.session.commit()
        flash("Data was edited successfully!")
        return redirect(url_for('post',id=post.id))
    form.title.data=post.title
    form.author.data=post.author
    form.content.data=post.content
    form.slug.data=post.slug
    return render_template('edit_post.html',form=form)

#Post View
@app.route('/posts/<int:id>')
def post(id):
    post=Posts.query.get_or_404(id)
    return render_template("post.html",post=post)

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
            user = Users(name=form.name.data,username=form.username.data, email=form.email.data,favourite_color=form.favourite_color.data,password_hash=hashed_pw) 
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data=''
        form.username.data=''
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

    


