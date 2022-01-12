from enum import unique
from flask import Flask,render_template,flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms import validators
from  wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create a Flask Intsance
app = Flask(__name__)

#Add to database SQLITE
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'\

#MySql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:BOSS97kills!@localhost/our_users'

#Secrete Key!
app.config['SECRET_KEY'] = 'any secret string'

#Initilise the database
db = SQLAlchemy(app)


#Create a model
class Users(db.Model):
    id =  db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200), nullable = False)
    email = db.Column(db.String(120), nullable = False, unique=True)
    date_added = db.Column(db.DateTime, default= datetime.utcnow)

    #Create A String
    def __rep__(self):
        return '<Name %r>' % self.name


#Create a Form Class
class UserForm(FlaskForm):
    name=StringField("Name",validators=[DataRequired()])
    email=StringField("E-mail",validators=[DataRequired()])
    submit = SubmitField("submit")
    

#Create a Form Class
class NamerForm(FlaskForm):
    name=StringField("Whats your name",validators=[DataRequired()])
    submit=SubmitField("Submit")



#Create a route Decorator
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

@app.route('/user/add',methods=['GET','POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()  

        if user is None:
            user = Users(name=form.name.data, email=form.email.data) 
            db.session.add(user)
            db.session.commit()

        name = form.name.data
        form.name.data=''
        form.email.data=''
        flash("User added successfully")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html",
                            form=form,
                            name=name,
                            our_users= our_users)

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name =name )
    #second commit

#Bank_statement
@app.route('/bank')
def bank():
    return render_template('bank_statement.html')

#Create custom error pages

#Invalid URL 
@app.errorhandler(404) 
def page_not_found(e):
    return render_template("404.html"),404


#Internal Servererro 
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"),500

#Create  a Name Page
@app.route('/name',methods=['GET','POST'])
def name():
    name = None
    form = NamerForm()

    # Validate Form
    if form.validate_on_submit():
        name = form.name.data
        flash(form.name.data +" your name has been submited Succefully!")
        form.name.data= ''
 
    return render_template('name.html',
    name = name,
    form = form)

    


