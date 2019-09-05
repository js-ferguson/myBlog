import os
from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('NOFOLIO_SECRET_KEY')
app.config["MONGO_URI"] = os.environ.get('MONGO_MYBLOG_URI')
app.config["MONGO_DBNAME"] = 'myBlog'

mongo = PyMongo(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'danger'

from myBlog import routes