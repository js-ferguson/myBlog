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


app.config['MAIL_SERVER'] = 'in-v3.mailjet.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'cf1cf5a5dd813f2bddff29daae40a219'  #os.environ.get('MAILJET_USER')
app.config['MAIL_PASSWORD'] = '435903d676101d3ac93c31cc0ffd627b'  #os.environ.get('MAILJET_PASS')
#MAIL_DEFAULT_SENDER = 'jw.akupunktur@gmail.com'
mail = Mail(app)


from myBlog import routes