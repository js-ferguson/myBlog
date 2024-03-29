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
import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config(
    cloud_name = os.environ.get('NOFOLIO_CLOUDINARY_CLOUD_NAME'),
    api_key = os.environ.get('NOFOLIO_CLOUDINARY_API_KEY'),
    api_secret = os.environ.get('NOFOLIO_CLOUDINARY_API_SECRET'),
    upload_preset = os.environ.get('NOFOLIO_CLOUDINARY_UPLOAD_PRESET')
)


users = mongo.db.users
posts = mongo.db.posts
comment = mongo.db.comment
portfolio = mongo.db.portfolio
current_project = mongo.db.current_project
posts_per_page = 8


def admin_user():
    '''
    Test if the current user is an admin
    '''
    admin_user = users.find_one(
        {'$and': [{'username': current_user.get_id()}, {'admin': True}]})
    return admin_user


def get_current_users_id():
    '''
    Returns the current users id.
    '''
    user = users.find_one({'username': current_user.get_id()})
    return user['_id']


def is_comment_author(user, comment_id):
    '''
    Test if the the current user is the author of a comment.
    '''
    is_author = comment.find_one(
        {'$and': [{'_id': ObjectId(comment_id)}, {'user': ObjectId(user)}]})
    if is_author:
        return True


def is_sticky():
    '''
    Test the sticky status of a post.
    '''
    sticky = posts.find_one({"sticky": True})
    return sticky


def posts_with_comment_count(page):
    '''
    Aggregation pipline that adds a comment count field to a post document.
    Posts are sorted so the newest is diplayed first and the output is paginated.
    '''
    # This pipeline (up to but not including the facet) was provided by user chridam on stackoverflow in respose to a question I posted
    # The facet came from stack overflow user Alex Blex, links in references.
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
    ag_posts = list(posts.aggregate(pipeline))
    return ag_posts


@app.route("/")
@app.route("/home")
@app.route("/index")
def home():
    """
    Create a view that returns the route for the landing page for /, /home and /index
    """
    form = EditProject()
    page = request.args.get('page', 1, type=int)
    data = posts_with_comment_count(page)

    def get_page_count():
        for item in data:
            post_count = item['metadata'][0]['total']
            page_count = post_count/posts_per_page
            return int(math.ceil(page_count))

    def create_num_list():
        '''
        Create a list of page numbers and None values for forum style page navigation buttons at the bottom of the post feed
        '''
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

    project = current_project.find_one(
        {'current_project': 'current_project'})
    tags = " ".join(project['tech_tags'])

    if request.method == 'GET':
        form.title.data = project['project_name']
        form.description.data = project['desc']
        tag_str = ' '.join(project['tech_tags'])
        form.tags.data = tag_str

    def posts():
        for post in data:
            return post['data']

    return render_template('home.html', posts=posts(), form=form,
                           admin_user=admin_user(), project=project, tags=tags, page=page,
                           page_links=create_num_list(), last_page=get_page_count(),
                           is_sticky=is_sticky(), flash=flash)


@app.route("/register", methods=['GET', 'POST'])
def register():
    '''
    Create a route that returns the registration page, allowing users to register on the site
    '''
    form = RegistrationForm()

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if form.validate_on_submit():
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
    '''
    Create a route that returns the login page that allows users to log in, 
    if they have previously registered an account
    '''
    form = LoginForm()

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if form.validate_on_submit():
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
    '''
    Log out the user and redirect to the landing page
    '''
    logout_user()
    return redirect(url_for('home'))


@app.route("/new_post")
@login_required
def new_post():
    '''
    Returns the new post page to allow a user to make a new post if they are logged in as an admin. 
    '''
    form = NewPostForm()

    if not admin_user():
        flash("You do not have permission to make new posts", "info")
        return redirect(url_for('home'))
    return render_template('new_post.html', form=form, posts=posts.find())


@app.route("/insert_post", methods=['POST'])
@login_required
def insert_post():
    '''
    Create a route that accepts new posts. Posts may optionally be marked as sticky.
    Must be logged in as an admin.
    '''
    author = users.find_one({'username': current_user.get_id()})
    post_author = author['_id']
    post_is_sticky = request.form.get('sticky')
    new_doc = {'title': request.form.get('title'),
               'post_author': post_author,
               'tags': [],
               'content': request.form.get('content'),
               'date_posted': datetime.utcnow(),
               'images': [],
               'sticky': False}

    # If new post is sticky, we set sticky: False on all previously sticky posts and change the new_doc to be sticky:True
    if post_is_sticky:
        posts.update_many({"sticky": True}, {"$set":
                                             {"sticky": False}
                                             }, upsert=True)
        new_doc['sticky'] = True
    
    if admin_user():
        try:
            posts.insert_one(new_doc)            
            posts.delete_many({"title": {"$exists": False}}) # removes empty posts that get created under certain conditions
            flash('Your new post has been successfully created', 'info')
        except:
            flash("Error accessing the database", "danger")
    else:
        flash("Only admin users may create posts.", "info")
    return redirect(url_for('home'))


@app.route("/post/<post_id>")
def post(post_id):
    '''
    Create a route that returns a view of a single blog post. 
    If the user is an admin, content controls will also be displayed
    '''
    form = NewCommentForm()
    has_comments = comment.count({'post_id': ObjectId(post_id)})
    comments = comment.find({'post_id': ObjectId(post_id)}).sort("_id", -1)
    post = posts.find_one_or_404({'_id': ObjectId(post_id)})

    def get_comment_username(user_id):
        user = users.find_one({'_id': ObjectId(user_id)})
        return user['username']

    return render_template('view_post.html', post=post, form=form, admin_user=admin_user(),
                           comments=comments, has_comments=has_comments,
                           get_comment_username=get_comment_username)


@app.route("/post/<post_id>/delete_comment", methods=['GET', 'POST'])
@login_required
def delete_comment(post_id):
    '''
    Create a route do delete a comment. Must be either the comment author or an admin.
    '''
    del_comment = request.args.get('comment_id')
    query = {'_id': ObjectId(del_comment)}

    if not is_comment_author(get_current_users_id(), del_comment) and not admin_user():
        flash('You do not have permission to remove this comment', 'info')
    else:
        comment.delete_one(query)
        flash('Your comment has been deleted', 'info')
    return redirect(url_for('post', post_id=post_id))


@app.route("/home/update_project", methods=['POST'])
@login_required
def update_project():
    '''
    Create a route to up update the Currently in Development box on the landing page
    '''
    form = EditProject()
    tag_list = list(form.tags.data.split(" "))
    new_doc = {
        'project_name': form.title.data, 'desc': form.description.data,
        'tech_tags': tag_list, 'current_project': 'current_project'
    }

    current_project.update({'current_project': 'current_project'}, new_doc)
    return redirect(url_for('home'))


@app.route("/post/<post_id>", methods=['POST'])
@login_required
def insert_comment(post_id):
    '''
    Create a route to allow users to make comments on posts
    '''
    author = users.find_one({"username": current_user.get_id()})
    new_doc = {'user': author['_id'], 'post_id': ObjectId(post_id), 'title': request.form.get('title'),
               'content': request.form.get('content'),
               'date_posted': datetime.utcnow()
               }

    comment.insert_one(new_doc)
    flash('Your comment was successfully posted', 'info')
    return redirect(url_for('post', post_id=post_id))


@app.route("/post/<post_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    '''
    Create a route to allow a user to edit a post or change its sticky status. 
    Must be the author of the post.
    '''
    post = posts.find_one_or_404({'_id': ObjectId(post_id)})
    author = users.find_one({'username': current_user.get_id()})
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
        update_doc = {"title": title, "content": content, "sticky": False}

        #If post is edited to be sticky, remove sticky from all other posts and add sticky: True to update_doc
        if post_is_sticky:
            posts.update_many({"sticky": True}, {"$set":
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
    '''
    Create a route to allow a user to delete a post.
    Must be an admin.
    '''
    query = {'_id': ObjectId(post_id)}

    if not admin_user():
        abort(403)

    posts.delete_one(query)
    flash('Your post has been deleted', 'info')
    return redirect(url_for('home'))

def save_images(images):
    '''
    takes a list of images and renames each with a random string. 
    Resizes images to a max of 500x500px and saved temporarily to static/images/project_files.
    Files are uploaded to cloudinary and their urls are returned as a list. 
    '''
    file_filenames = []
    save_paths = []
    cloud_file_list = []

    for image in images:
        if image:
            rand_hex = secrets.token_hex(8)
            _, f_ext = os.path.splitext(image.filename)
            file_filenames.append(rand_hex + f_ext)

    for name in file_filenames:
        save_paths.append(os.path.join(
            app.root_path, 'static/images/project_pics', name))

    for image, path in zip(images, save_paths):
        if image:
            i = Image.open(image)
            (width, height) = (500, 500)
            i.thumbnail((width, height))
            i.save(path)
            cloud_image = cloudinary.uploader.unsigned_upload(path, os.environ.get('NOFOLIO_CLOUDINARY_UPLOAD_PRESET'))
            cloud_file_list.append(cloud_image['secure_url'])                        
    return cloud_file_list


@app.route("/portfolio", methods=['GET', 'POST'])
def portfolio():
    '''
    Create a route that returns the portfolio page and allows users to add a new
    portfolio item via a modal form.
    '''
    form = NewPortfolioProject()
    projects = mongo.db.portfolio.find()
    image_files = []
    cloud_saves = []

    def sort_portfolio():
        proj = []
        for project in projects:
            proj.append(project)
        proj.reverse()
        return proj

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

        mongo.db.portfolio.insert_one(new_doc)
        flash('Your new project has been added to your portfolio', 'info')
        return redirect(url_for('portfolio'))
    return render_template('portfolio.html', projects=sort_portfolio(), form=form, admin_user=admin_user(), image_files=image_files)


@app.route("/portfolio/delete", methods=['GET', 'POST'])
@login_required
def delete_project():
    '''
    Create a route that allows an admin user to delete a portfolio item.
    Also deletes files associated with the project from cloudinary by pulling the public_key from the files url in the db
    and passing it to the cloudinary destroy method
    '''
    project = request.args.get('project_id')
    query = {'_id': ObjectId(project)}
    port_proj = mongo.db.portfolio.find_one(query)

    if not admin_user():
        flash("You do not have permission to remove projects", "info")
        return redirect(url_for('portfolio'))

    for url in port_proj['images']:
        public_key = url[url.rfind("/")+1:]
        cloudinary.uploader.destroy(public_key)
    
    mongo.db.portfolio.delete_one(query)
    flash('Your project has been deleted', 'info')
    return redirect(url_for('portfolio'))


@app.route("/account", methods=['POST', 'GET'])
@login_required
def account():
    '''
    Create an account that allows users to access a user profile page and lets them update their user details.
    '''
    form = AccountUpdateForm()
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


def get_reset_token(user, expires_sec=1800):
    '''
    Create a time limited password reset token by serialising a tuple with the users user_id 
    '''
    s = Serialiser(app.config['SECRET_KEY'], expires_sec)
    user_id = str(user['_id'])
    return s.dumps({'user_id': user_id}).decode('utf-8')


def validate_reset_token(token):
    '''
    Validate the token and return the user with a matching user_id
    '''
    s = Serialiser(app.config['SECRET_KEY'])

    try:
        user_id = s.loads(token)['user_id']
    except:
        return None
    return users.find_one({'_id': ObjectId(user_id)})


def send_reset_email(user):
    '''
    Send an email to the user. Email contains url with an embeded token
    '''
    token = get_reset_token(user)
    msg = Message('Password reset request', sender=os.environ.get(
        'SENDER_EMAIL'), recipients=[user['email']])
    msg.body = f'''To reset your password go to the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not request a new password, you can safely ignore this email
'''
    mail.send(msg)


@app.route("/reset_password", methods=['POST', 'GET'])
def reset_request():
    '''
    Create a route that returns the new password page, allowing the user to request a password reset
    '''
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        user = users.find_one({'email': form.email.data})
        send_reset_email(user)
        flash('Check your email for instructions to reset your password', 'info')
        return redirect(url_for('login'))
    return render_template('new_password.html', form=form)


@app.route("/reset_password/<token>", methods=['POST', 'GET'])
def reset_token(token):
    '''
    Create a route that is accessed when the user clicks the link in the reset password email.
    Token is passed to the function via a url parameter.
    '''
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = validate_reset_token(token)

    if user is None:

        flash('That is an invalid or expired token', 'danger')
        return redirect(url_for('reset_request'))
    form = NewPasswordForm()
    if form.validate_on_submit():
        hashpass = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        users.update_one({'_id': user['_id']}, {
                         '$set': {'password': hashpass}})
        flash('Your password has been updated', 'info')
        return redirect(url_for('login'))
    return render_template('token_password.html', form=form)
