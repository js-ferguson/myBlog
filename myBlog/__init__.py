import os
from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('NOFOLIO_SECRET_KEY')
app.config["MONGO_URI"] = os.environ.get('MONGO_MYBLOG_URI')
app.config["MONGO_DBNAME"] = 'myBlog'

mongo = PyMongo(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'danger'

#Set-cookie CSFR options
#app.config['SESSION_COOKIE_SECURE'] = True
#app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ.get('SENDGRID_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('SENDGRID_PASS')
mail = Mail(app)

from myBlog import routes