import os
import math
from itsdangerous import TimedJSONWebSignatureSerializer as Serialiser
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from datetime import datetime
from myBlog import app, mongo, bcrypt, mail
from bson.objectid import ObjectId
from myBlog.forms import (RegistrationForm, LoginForm, NewPostForm, AccountUpdateForm, EditProject, 
                          PostReplyForm, NewCommentForm, EditProject, NewPortfolioProject, 
                          NewPasswordForm, ResetPasswordForm)
from myBlog.login import User
from flask_login import current_user, login_user, logout_user, login_required
import secrets
from PIL import Image
from flask_mail import Message


posts_per_page = 5

def admin_user():
    '''Determine if the current use has admin privelages'''
    admin_user = mongo.db.users.find_one(
        {'$and': [{'username': current_user.get_id()}, {'admin': True}]})
    return admin_user

def get_current_users_id():
    user = mongo.db.users.find_one({'username': current_user.get_id()})
    return user['_id']

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
            "data": [{"$skip": (page - 1)*posts_per_page}, {"$limit": posts_per_page}]
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

    def get_page_count():
        for item in data:
            post_count = item['metadata'][0]['total']
            page_count = post_count/posts_per_page
            return int(math.ceil(page_count))

    def create_num_list():
        '''Create a list of page numbers and None values for a forum style page nav'''
        num_list = []

        for num in range(1, (get_page_count() + 1)):

            if num == (page - 2) or num == (page - 1):
                num_list.append(num)
                continue
            if num == page:
                num_list.append(num)
                continue
            if num == (page + 1) or num == (page + 2):
                num_list.append(num)
                continue
            else:
                num_list.append(None)
        for num in num_list:
            if num == page:
                del num_list[0]
            if num == get_page_count() - 1:
                del num_list[-1]
            if num == get_page_count():
                del num_list[-1]

        # remove consecutive duplicate None values
        i = 0
        while i < len(num_list) - 1:
            if num_list[i] == num_list[i+1]:
                del num_list[i]
            else:
                i = i+1
        return num_list

    if page == get_page_count():
        flash("You have reached the last page", "info")

    project = mongo.db.current_project.find_one(
        {'current_project': 'current_project'})
    tags = " ".join(project['tech_tags'])

    def posts():
        for post in data:
            return post['data']

    return render_template('home.html', posts=posts(), form=form,
                           admin_user=admin_user(), project=project, tags=tags, page=page,
                           page_links=create_num_list(), last_page=get_page_count(),
                           is_sticky=is_sticky(), flash=flash)


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
                    'password': hashpass, 'email': form.email.data, 'firstname': '', 'lastname': ''}
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
            login_user(user_obj, remember=form.remember.data)
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
    new_doc = {'title': request.form.get('title'),
               'post_author': post_author,
               'tags': [],
               'content': request.form.get('content'),
               'date_posted': datetime.utcnow(),
               'images': [],
               'sticky': False}

    if post_is_sticky:
        mongo.db.posts.update_many({"sticky": True}, {"$set":
                                                      {"sticky": False}
                                                      }, upsert=True)
        new_doc['sticky'] = True

    try:
        posts.insert_one(new_doc)
        posts.delete_many({"title": {"$exists": False}})
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
                           comments=comments, has_comments=has_comments,
                           get_comment_username=get_comment_username)


def is_comment_author(user, comment_id):
    #author = mongo.db.posts.find_one({"post_author": user})
    #comment = mongo.db.comment.find_one({'_id': comment_id})
    is_author = mongo.db.comment.find_one({'$and': [{'_id': ObjectId(comment_id)}, {'user': ObjectId(user)}]})
    if is_author:
        return True


@app.route("/post/<post_id>/delete_comment", methods=['GET', 'POST'])
@login_required
def delete_comment(post_id):
    comment = request.args.get('comment_id')
    query = {'_id': ObjectId(comment)}

    #if not admin_user():
    #    abort(403)
    if not is_comment_author(get_current_users_id(), comment) and not admin_user():
        flash('You do not have permission to remove this comment', 'info')
    else:
        mongo.db.comment.delete_one(query)
        flash('Your comment has been deleted', 'info')
    return redirect(url_for('post', post_id=post_id))


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
        
    elif request.method == 'POST':
        content = request.form.get("content")
        title = request.form.get("title")
        posts = mongo.db.posts
        update_doc = {"title": title, "content": content, "sticky": False}
        if post_is_sticky:
            mongo.db.posts.update_many({"sticky": True}, {"$set":
                                                          {"sticky": False}
                                                          }, upsert=True)
            update_doc["sticky"] = True
        
        posts.find_one_and_update(
            {"_id": ObjectId(post_id)},
            {"$set": update_doc},
            upsert=True
        )
        posts.delete_many({"title": {"$exists": False}})
        flash('Your blog post has been updated', 'info')
        return redirect(url_for('home'))
    return render_template('edit_post.html', form=form, post=post, admin_user=admin_user())


@app.route("/post/<post_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    query = {'_id': ObjectId(post_id)}

    if not admin_user():
        abort(403)

    mongo.db.posts.delete_one(query)
    flash('Your post has been deleted', 'info')
    return redirect(url_for('home'))


def save_images(images):
    file_filenames = []
    save_paths = []

    for image in images:
        rand_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(image.filename)
        file_filenames.append(rand_hex + f_ext)

    for name in file_filenames:
        save_paths.append(os.path.join(
            app.root_path, 'static/images/project_pics', name))

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

    def sort_portfolio():
        proj = []
        for project in projects:
            proj.append(project)
        proj.reverse()
        return proj

    #projs = sort_portfolio().reverse()

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

    return render_template('portfolio.html', projects=sort_portfolio(), form=form, admin_user=admin_user(), image_files=image_files)


@app.route("/portfolio/delete", methods=['GET', 'POST'])
@login_required
def delete_project():
    project = request.args.get('project_id')
    query = {'_id': ObjectId(project)}
    port_proj = mongo.db.portfolio.find_one(query)

    if not admin_user():
        flash("You do not have permission to remove projects", "info")
        return redirect(url_for('portfolio'))

    for image in port_proj['images']:
        os.remove(app.root_path + '/static/images/project_pics/' + image)

    mongo.db.portfolio.delete_one(query)
    flash('Your project has been deleted', 'info')
    return redirect(url_for('portfolio'))   


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
    users = mongo.db.users
    user = users.find_one({'username': current_user.username})

    if request.method == 'GET':
        form.username.data = user['username']
        form.email.data = user['email']
        if user['firstname']:
            form.firstname.data = user['firstname']
        else:
            form.firstname.data = ""
        if user['lastname']:
            form.lastname.data = user['lastname']
        else:
            form.lastname.data = ""

    if form.validate_on_submit():
        new_doc = {"firstname": form.firstname.data,
                   "lastname": form.lastname.data,
                   "username": form.username.data,
                   "email": form.email.data
                   }

        users.update_one({'username': current_user.username},
                         {"$set": new_doc}, upsert=True)
        flash('Your details have been updated, please log in again', 'info')
        return redirect(url_for('login'))
    return render_template('account.html', form=form)


def get_reset_token(user, expires_sec=1800): #5. takes the user and generates a token 
    s = Serialiser(app.config['SECRET_KEY'], expires_sec)
    user_id = str(user['_id'])     
    return s.dumps({'user_id': user_id}).decode('utf-8')


def validate_reset_token(token):
    s = Serialiser(app.config['SECRET_KEY'])   
    
    try:     
        user_id = s.loads(token)['user_id']      
    except:
        return None
    return mongo.db.users.find_one({'_id': ObjectId(user_id)})


def send_reset_email(user): 
    token = get_reset_token(user)
    msg = Message('Password reset request', sender='jw.akupunktur@gmail.com', recipients=[user['email']])
    msg.body = f'''To reset your password go to the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not request a new password, you can safely ignore this email
'''
    mail.send(msg)


@app.route("/reset_password", methods=['POST', 'GET'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({'email': form.email.data}) # 1. finds the user whose email matched
        send_reset_email(user) #2. call send_reset_email with the user we found.
        
        flash('Check your email for instructions to reset your password', 'info')
        return redirect(url_for('login'))
    return render_template('new_password.html', form=form)


@app.route("/reset_password/<token>", methods=['POST', 'GET'])
def reset_token(token):
    
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = validate_reset_token(token)
    
    if user is None:
        
        flash('That is an invalid or expired token', 'danger')
        return redirect(url_for('reset_request'))
    form = NewPasswordForm()
    if form.validate_on_submit():
        users = mongo.db.users
        hashpass = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')        
        users.update_one({'_id': user['_id']}, {'$set': {'password': hashpass}})
        flash('Your password has been updated', 'info')
        return redirect(url_for('login'))
    return render_template('token_password.html', form=form)