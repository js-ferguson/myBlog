#from flask_login import current_user, login_user, logout_user, login_required
from myBlog import mongo, login_manager

 

class User:
    def __init__(self, username):
        self.username = username

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.username

    #@staticmethod
    #def check_password(password_hash, password):
    #    return check_password_hash(password_hash, password)


@login_manager.user_loader
def load_user(username):
    user = mongo.db.users.find_one({"username": username})
    if not user:
        return None
    return User(username=user['username'])