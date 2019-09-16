from flask import render_template, url_for, flash, redirect, request, abort
from datetime import datetime
from myBlog import app, mongo, bcrypt
from bson.objectid import ObjectId
from myBlog.forms import RegistrationForm, LoginForm, NewPostForm, AccountUpdateForm, EditProject, PostReplyForm, NewCommentForm, EditProject
from myBlog.login import User
from flask_login import current_user, login_user, logout_user, login_required


def admin_user():
    admin_user = mongo.db.users.find_one(
        {'$and': [{'username': current_user.get_id()}, {'admin': True}]})
    return admin_user


def posts_with_comment_count():
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
        {"$sort": {"_id": -1}}
    ]
    posts = list(mongo.db.posts.aggregate(pipeline))
    return posts


@app.route("/")
@app.route("/home")
def home():
    form = EditProject()
    project = mongo.db.current_project.find_one({'current_project': 'current_project'})
    tags = " ".join(project['tech_tags'])
    return render_template('home.html', posts=posts_with_comment_count(), form=form, admin_user=admin_user(), project=project, tags=tags)


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
    # if form.validate_on_submit():
    return render_template('new_post.html', form=form, posts=mongo.db.posts.find())


@app.route("/insert_post", methods=['POST'])
def insert_post():
    posts = mongo.db.posts
    author = mongo.db.users.find_one({'username': current_user.get_id()})
    post_author = author['_id']
    # posts.insert_one(request.form.to_dict())

    new_doc = {'title': request.form.get('title'), 'post_author': post_author,
               'tags': [], 'content': request.form.get('content'),
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
    form = NewCommentForm()
    has_comments = mongo.db.comment.count({'post_id': ObjectId(post_id)})
    #comment_username = get_comment_username()
    comments = mongo.db.comment.find(
        {'post_id': ObjectId(post_id)}).sort("_id", -1)
    post = mongo.db.posts.find_one_or_404({'_id': ObjectId(post_id)})

    def get_comment_username(user_id):
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        return user['username']

    return render_template('view_post.html', post=post, form=form, admin_user=admin_user(),
                           comments=comments, has_comments=has_comments, get_comment_username=get_comment_username )

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
               'date_posted': datetime.utcnow()}
    comments.insert_one(new_doc)
    flash('Your comment was successfully posted', 'info')
    return redirect(url_for('post', post_id=post_id))


@app.route("/post/<post_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = mongo.db.posts.find_one_or_404({'_id': ObjectId(post_id)})
    author = mongo.db.users.find_one({'username': current_user.get_id()})
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
        # try:
        posts = mongo.db.posts
        posts.find_one_and_update(
            {"_id": ObjectId(post_id)},
            {"$set":
                {"title": title, "content": content}
             }, upsert=True
        )
        flash('Your blog post has been updated', 'info')
    return redirect(url_for('home'))


@app.route("/account", methods=['POST', 'GET'])
@login_required
def account():
    form = AccountUpdateForm()
    return render_template('account.html', form=form)
