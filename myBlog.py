import os
from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from forms import RegistrationForm, LoginForm, NewPostForm
import bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = '1f67b3678156205853ddc3ef59abafed'
app.config["MONGO_URI"] = os.environ.get('MONGO_MYBLOG_URI')
app.config["MONGO_DBNAME"] = 'myBlog'

mongo = PyMongo(app)


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=mongo.db.posts.find()) #post=mongo is used as an argument here to pass the content of posts into the template so we can access the posts variable


@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/portfolio")
def portfolio():
    return render_template('portfolio.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        users = mongo.db.users
        existing_user = users.find_one({'username': request.form['username']})
        
        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'username': request.form['username'], 'password' : hashpass, 'email': request.form['email']})
            session['username'] = request.form['username']
            flash(f'Account created for {form.username.data}!', 'info')
            return redirect(url_for('login'))
        
        flash(f'Username already taken', 'info')
        return redirect(url_for('register'))

        
        
    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == "admin@myBlog.com" and form.password.data == 'password':
            flash(f'{form.email.data}, you have been logged in!', 'info')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)


@app.route("/new_post")
def new_post():
    form = NewPostForm()
    #if form.validate_on_submit():
    return render_template('new_post.html', form=form, posts=mongo.db.posts.find())


@app.route("/insert_post", methods=['POST'])
def insert_post():
    posts = mongo.db.posts
    #posts.insert_one(request.form.to_dict())    

    new_doc = {'title': request.form.get('title'), 'tags': [], 'content': request.form.get('content'),
               'date_posted': "", "images": []}
    try:
        posts.insert_one(new_doc)
        print("")
        print("Document inserted")
    except:
        print("Error accessing the database")    
    
    return redirect(url_for('home'))



if __name__ == '__main__':
    app.run(debug=True)
