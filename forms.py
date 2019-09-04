from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError



class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=6, max=20)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        users = mongo.db.users
        existing_user = users.find_one({'username': request.form['username']})
        if existing_user:
            raise ValidationError('That username is already taken.')

    def validate_email(self, email):
        users = mongo.db.users
        existing_user = users.find_one({'email': request.form['email']})
        if existing_user:
            raise ValidationError('That email address is already in use.')
    

class LoginForm(FlaskForm):
    
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=6, max=20)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class NewPostForm(FlaskForm):

    title = StringField('Title',
                        validators=[DataRequired(), Length(min=1, max=50)])
    content = TextAreaField('Content', 
                        validators=[DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField('Save Post')