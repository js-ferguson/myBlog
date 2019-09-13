from flask import render_template, url_for, flash, redirect, request, abort
from datetime import datetime
from myBlog import app, mongo, bcrypt
from bson.objectid import ObjectId
from myBlog.forms import RegistrationForm, LoginForm, NewPostForm, AccountUpdateForm, EditProject, PostReplyForm
from myBlog.login import User
from flask_login import current_user, login_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    form = EditProject()
    posts = mongo.db.posts.find().sort("_id", -1)
    admin_user = mongo.db.users.find_one( {'$and': [ {'username': current_user.get_id() }, {'admin': True} ] } )
    return render_template('home.html', posts = posts, form = form, admin_user = admin_user)


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
        new_user = {'username': form.username.data, 'password': hashpass, 'email': form.email.data}
        users.insert(new_user)
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
    author = mongo.db.users.find_one( { 'username': current_user.get_id() } )
    post_author = author['_id']
    # posts.insert_one(request.form.to_dict())

    new_doc = {'title': request.form.get('title'),'post_author': post_author, 'tags': [], 'content': request.form.get('content'),
               'date_posted': datetime.utcnow(), "images": []}
    try:
        posts.insert_one(new_doc)
        print("")
        print("Document inserted")
    except:
        print("Error accessing the database")

    return redirect(url_for('home'))

@app.route("/post/<post_id>")
def post(post_id):
    form=NewPostForm()
    post = mongo.db.posts.find_one_or_404({'_id': ObjectId(post_id)})
    #post_id_string = str(post['_id'])
    return render_template('view_post.html', post=post, form=form)


@app.route("/post/<post_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_post(post_id):    
    post = mongo.db.posts.find_one_or_404({'_id': ObjectId(post_id)})
    author = mongo.db.users.find_one( { 'username': current_user.get_id() } )
    if post['post_author'] != author['_id']:
        abort(403)
    form = NewPostForm()
    if request.method == 'GET':
        form.title.data = post['title']
        form.content.data = post['content']
        return render_template('edit_post.html', form=form, post=post, admin_user=admin_user)
    
    elif request.method == 'POST':
        content = request.form.get("content")
        title = request.form.get("title")
        print(content)
        #try:
        posts = mongo.db.posts 
        posts.find_one_and_update(
            {"_id" : ObjectId(post_id)},
            {"$set":
                {"title": title, "content": content}
            },upsert=True
        )
        flash('Your blog post has been updated', 'info')
    return redirect(url_for('home'))
        
    
@login_required
@app.route("/post/<post_id>/comment", methods=['GET', 'POST'])
def comment(post_id):
    


    return redirect(url_for('post'))




@app.route("/account", methods=['POST', 'GET'])
@login_required
def account():
    form = AccountUpdateForm()
    return render_template('account.html', form=form)
