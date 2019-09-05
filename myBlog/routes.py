from flask import render_template, url_for, flash, redirect, request
from myBlog import app, mongo, bcrypt
from bson.objectid import ObjectId
from myBlog.forms import RegistrationForm, LoginForm, NewPostForm
from myBlog.login import User
from flask_login import current_user, login_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    #if User.is_authenticated:
     #   flash(f'You are logged in as {User.username}', 'info')

    # post=mongo is used as an argument here to pass the content of posts into the template so we can access the posts variable
    return render_template('home.html', posts=mongo.db.posts.find())


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/portfolio")
def portfolio():
    return render_template('portfolio.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        users = mongo.db.users
        hashpass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        users.insert({'username': form.username.data, 'password': hashpass, 'email': form.email.data})
        flash('Your account has been created. Log in to continue', 'info')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        users = mongo.db.users
        user = users.find_one({'email': form.email.data})
        #userpass = mongo.db.users.find_one({'email': form.email.data}, {'password': 1, '_id': 0})
        if user and bcrypt.check_password_hash(user['password'], form.password.data):
            user_obj = User(username=user['username'])
            login_user(user_obj)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login was unsuccessful, wrong email/password', 'danger')        
    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))



@app.route("/new_post")
@login_required
def new_post():
    form = NewPostForm()
    # if form.validate_on_submit():
    return render_template('new_post.html', form=form, posts=mongo.db.posts.find())


@app.route("/insert_post", methods=['POST'])
def insert_post():
    posts = mongo.db.posts
    # posts.insert_one(request.form.to_dict())

    new_doc = {'title': request.form.get('title'), 'tags': [], 'content': request.form.get('content'),
               'date_posted': "", "images": []}
    try:
        posts.insert_one(new_doc)
        print("")
        print("Document inserted")
    except:
        print("Error accessing the database")

    return redirect(url_for('home'))

@app.route("/single_post/<_id>")
def single_post():
    return render_template('single_post.html')