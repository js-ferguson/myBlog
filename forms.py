from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email(message="Invalid email"), Length(max=30)])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=8, max=20)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    

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
    content = StringField('Content',
                        validators=[DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField('Save Post')