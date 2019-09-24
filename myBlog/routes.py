import os
import math 
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from datetime import datetime
from myBlog import app, mongo, bcrypt
from bson.objectid import ObjectId
from myBlog.forms import RegistrationForm, LoginForm, NewPostForm, AccountUpdateForm, EditProject, PostReplyForm, NewCommentForm, EditProject, NewPortfolioProject
from myBlog.login import User
from flask_login import current_user, login_user, logout_user, login_required
import secrets
from PIL import Image


def admin_user():
    '''Determine if the current use has admin privelages'''
    admin_user = mongo.db.users.find_one(
        {'$and': [{'username': current_user.get_id()}, {'admin': True}]})
    return admin_user

def is_sticky():
        sticky = mongo.db.posts.find_one({"sticky": True})
        return sticky

def posts_with_comment_count(page):    
    pipeline = [
        {"$lookup": {
            "from": "comment",
            "localField": "_id",
            "foreignField": "post_id",
            "as": "comment_count"
        }},
        {"$addFields": {
            "comment_count": {"$size": "$comment_count"}
        }},
        {"$sort": {"_id": -1}}, 
        {'$facet': { 
            "metadata": [{"$count": "total"}, {"$addFields": {"page": int(page)}}],
            "data": [{"$skip": (page - 1)*4}, {"$limit": 4}] # add projection here wish you re-shape the docs
            }}    
    ]
    posts = list(mongo.db.posts.aggregate(pipeline))
    return posts


@app.route("/")
@app.route("/home")
@app.route("/index")
def home():
    form = EditProject()
    page = request.args.get('page', 1, type=int)  
    data = posts_with_comment_count(page)

    print(is_sticky())

    def get_page_count():
        for item in data:
            post_count = item['metadata'][0]['total']
            page_count = post_count/4
            return int(math.ceil(page_count))    
    print(get_page_count())

    def create_num_list():
        '''Create a list of page numbers and None values for a forum style page nav'''
        num_list = []
        
        for num in range(1, (get_page_count() +1)):
            
            if num == (page -2) or num == (page -1):
                num_list.append(num)
                continue
            if num == page:
                num_list.append(num)
                continue
            if num == (page +1) or num == (page +2):
                num_list.append(num)
                continue
            else:
                num_list.append(None)
        for num in num_list:
            if num == page:
                del num_list[0]
            if num == get_page_count():
                del num_list[-1] 
        
        #remove consecutive duplicate None values
        i = 0
        while i < len(num_list) -1:
            if num_list[i] == num_list[i+1]:
                del num_list[i]
            else:
                i = i+1
        return num_list 
    
    print(create_num_list())
    
    project = mongo.db.current_project.find_one(
        {'current_project': 'current_project'})
    tags = " ".join(project['tech_tags'])

    def posts():
     for post in data:
        return post['data']        

    return render_template('home.html', posts=posts(), form=form,
        admin_user=admin_user(), project=project, tags=tags, page=page,
        page_links=create_num_list(), last_page=get_page_count(),
        is_sticky=is_sticky())


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        users = mongo.db.users
        hashpass = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        new_user = {'username': form.username.data,
                    'password': hashpass, 'email': form.email.data}
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
    return render_template('new_post.html', form=form, posts=mongo.db.posts.find())


@app.route("/insert_post", methods=['POST'])
def insert_post():
    posts = mongo.db.posts
    author = mongo.db.users.find_one({'username': current_user.get_id()})
    post_author = author['_id']
    post_is_sticky = request.form.get('sticky')

    if post_is_sticky:
        
        mongo.db.posts.update_many({"sticky": True}, {"$set":
                {"sticky": False}
             }, upsert=True)
        
        new_doc = {'title': request.form.get('title'), 'post_author': post_author,
                'tags': [], 'content': request.form.get('content'),
                'date_posted': datetime.utcnow(), "images": [], "sticky": True}

        
    else:
        new_doc = {'title': request.form.get('title'), 'post_author': post_author,
                'tags': [], 'content': request.form.get('content'),
                'date_posted': datetime.utcnow(), "images": [], "sticky": False}
    
    try:
        posts.insert_one(new_doc)
        print("")
        print("Document inserted")
    except:
        print("Error accessing the database")

    return redirect(url_for('home'))


@app.route("/post/<post_id>")
def post(post_id):
    form = NewCommentForm()
    has_comments = mongo.db.comment.count({'post_id': ObjectId(post_id)})
    comments = mongo.db.comment.find(
        {'post_id': ObjectId(post_id)}).sort("_id", -1)
    post = mongo.db.posts.find_one_or_404({'_id': ObjectId(post_id)})

    def get_comment_username(user_id):
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        return user['username']

    return render_template('view_post.html', post=post, form=form, admin_user=admin_user(),
                           comments=comments, has_comments=has_comments, get_comment_username=get_comment_username)


@app.route("/home/update_project", methods=['POST'])
@login_required
def update_project():
    project = mongo.db.current_project
    form = EditProject()
    tag_list = list(form.tags.data.split(" "))
    new_doc = {
        'project_name': form.title.data, 'desc': form.description.data,
        'tech_tags': tag_list, 'current_project': 'current_project'
    }

    project.update({'current_project': 'current_project'}, new_doc)
    return redirect(url_for('home'))


@app.route("/post/<post_id>", methods=['POST'])
@login_required
def insert_comment(post_id):
    comments = mongo.db.comment
    author = mongo.db.users.find_one({"username": current_user.get_id()})
    new_doc = {'user': author['_id'], 'post_id': ObjectId(post_id), 'title': request.form.get('title'),
               'content': request.form.get('content'),
               'date_posted': datetime.utcnow()
               }

    comments.insert_one(new_doc)
    flash('Your comment was successfully posted', 'info')
    return redirect(url_for('post', post_id=post_id))


@app.route("/post/<post_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = mongo.db.posts.find_one_or_404({'_id': ObjectId(post_id)})
    author = mongo.db.users.find_one({'username': current_user.get_id()})
    form = NewPostForm()
    post_is_sticky = request.form.get('sticky')

    if post['post_author'] != author['_id']:
        abort(403)    
    
    if request.method == 'GET':
        form.title.data = post['title']
        form.content.data = post['content']
        return render_template('edit_post.html', form=form, post=post, admin_user=admin_user())
    elif request.method == 'POST':
        content = request.form.get("content")
        title = request.form.get("title")          
        posts = mongo.db.posts
        if post_is_sticky:
            mongo.db.posts.update_many({"sticky": True}, {"$set":
                {"sticky": False}
             }, upsert=True)

            posts.find_one_and_update(
                {"_id": ObjectId(post_id)},
                {"$set":
                    {"title": title, "content": content, "sticky": True}
                }, upsert=True
            )
        else:
            posts.find_one_and_update(
                {"_id": ObjectId(post_id)},
                {"$set":
                    {"title": title, "content": content, "sticky": False}
                }, upsert=True
            )
        flash('Your blog post has been updated', 'info')
    return redirect(url_for('home'))


def save_images(images):
    file_filenames = []  # randomhex.jpg
    save_paths = []

    for image in images:
        rand_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(image.filename)
        file_filenames.append(rand_hex + f_ext)

    for name in file_filenames:
        save_paths.append(os.path.join(app.root_path, 'static/images/project_pics', name))

    for image, path in zip(images, save_paths):
        i = Image.open(image)
        (width, height) = (500, 500)
        i.thumbnail((width, height))
        i.save(path)
    return file_filenames


@app.route("/portfolio", methods=['GET', 'POST'])
def portfolio():

    form = NewPortfolioProject()
    portfolio = mongo.db.portfolio
    projects = portfolio.find()
    image_files = []

    if request.method == 'POST':
        tag_list = list(form.tags.data.split(" "))

    if form.images.data:
        image_files = save_images(form.images.data)
        new_doc = {
            'project_name': form.title.data,
            'desc': form.description.data,
            'tech_tags': tag_list,
            'link': form.link.data,
            'github_link': form.github_link.data,
            'images': image_files
        }

        portfolio.insert_one(new_doc)
        flash('Your new project has been added to your portfolio', 'info')
        return redirect(url_for('portfolio'))

    return render_template('portfolio.html', projects=projects, form=form, admin_user=admin_user(), image_files=image_files)


@app.route("/insert_project", methods=['POST'])
@login_required
def insert_project():
    form = NewPortfolioProject()
    portfolio = mongo.db.portfolio
    tag_list = list(form.tags.data.split(" "))

    if form.validate_on_submit():

        if form.images.data:
            image_files = save_images(form.images.data)
        new_doc = {
            'project_name': form.title.data,
            'desc': form.description.data,
            'tech_tags': tag_list,
            'link': form.link.data,
            'github_link': form.github_link.data,
            'images': image_files
        }

        portfolio.insert_one(new_doc)
        flash('Your new project has been added to your portfolio', 'info')
    return redirect(url_for('portfolio'))


@app.route("/account", methods=['POST', 'GET'])
@login_required
def account():
    form = AccountUpdateForm()
    return render_template('account.html', form=form)
