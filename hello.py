from flask import Flask,render_template

# Create a Flask Intsance
app = Flask(__name__)

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


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name =name )

#Create custom error pages

#Invalid URL 
@app.errorhandler(404) 
def page_not_found(e):
    return render_template("404.html"),404


#Internal Servererro 
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"),500