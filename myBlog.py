import os
from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect, request
from flask_login import LoginManager
from flask_pymongo import PyMongo

from pymongo import MongoClient
import mongoengine
from mongoengine import connect, Document
from bson.objectid import ObjectId
from forms import RegistrationForm, LoginForm, NewPostForm

from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = '1f67b3678156205853ddc3ef59abafed'

#app.config["MONGO_URI"] = os.environ.get('MONGO_MYBLOG_URI')
#app.config["MONGO_DBNAME"] = 'myBlog'
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
mongo_uri = os.environ.get('MONGO_MYBLOG_URI')
#mongo = PyMongo(app)

client = MongoClient(mongo_uri)
db = client.myBlog
connect('myBlog')

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=db.posts.find()) #post=mongo is used as an argument here to pass the content of posts into the template so we can access the posts variable


@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/portfolio")
def portfolio():
    return render_template('portfolio.html')

import mongoengine
from mongoengine import connect
from myBlog import login_manager


class User(db.Document):
    #meta = {'collection': 'users'}
    username = db.StringField(max_length=20)
    email = db.StringField(max_length=30)
    password = db.StringField()

@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            existing_user = User.objects(email=form.email.data).first()
            if existing_user is None:
                hash_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                hey = User(form.email.data, hash_pw).save()
                login_user(hey)
                return redirect(url_for('home'))
    return render_template('register.html', form=form)
    

    
    
    #if form.validate_on_submit():
    #    hash_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
     #   users = mongo.db.users
    #    new_doc = {'username': request.form.get('username'), 'email': request.form.get('email'), 'avatar_pic': ''
     #               'password': hash_pw}
    #    try:
     #       users.insert_one(new_doc)
     #       print("")
     #       flash('New post successfully created!', 'info')
      #  except:
     #       print("Error accessing the database")    
      #  
      #  flash(f'Account created for {form.username.data}!', 'info')
      #  return redirect(url_for('login'))
        
   # return render_template('register.html', form=form)


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
    return render_template('new_post.html', form=form, posts=db.posts.find())


@app.route("/insert_post", methods=['POST'])
def insert_post():
    posts = mongo.db.posts
    new_doc = {'title': request.form.get('title'), 'tags': [], 'content': request.form.get('content'),
               'date_posted': datetime.utcnow(), 'images': []}
    try:
        posts.insert_one(new_doc)
        print("")
        flash('New post successfully created!', 'info')
    except:
        print("Error accessing the database")    
    
    return redirect(url_for('home'))



if __name__ == '__main__':
    app.run(debug=True)
