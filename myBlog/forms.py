from flask import request, flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from myBlog import mongo


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=6, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        users = mongo.db.users
        existing_user = users.find_one({'username': username.data})
        if existing_user:
            raise ValidationError('That username is already taken.')

    def validate_email(self, email):
        users = mongo.db.users
        existing_user = users.find_one({'email': email.data})
        if existing_user:
            raise ValidationError('That email address is already in use.')


class LoginForm(FlaskForm):

    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=6, max=20)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class NewPostForm(FlaskForm):

    title = TextAreaField('Title', validators=[DataRequired(), Length(max=50)])
    content = TextAreaField('Content', validators=[
                            DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField('Save Post')


class AccountUpdateForm(FlaskForm):
    firstname = StringField('Firstname')
    lastname = StringField('Lastname')
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            users = mongo.db.users
            existing_user = users.find_one({'username': username.data})
            if existing_user:
                flash(f'The username {username.data} is already taken', 'danger')
                raise ValidationError('That username is already taken.')

    def validate_email(self, email):
        if email.data != current_user.email:
            users = mongo.db.users
            existing_user = users.find_one({'email': email.data})
            if existing_user:
                flash(f'The email {email.data} is already in use.', 'danger')
                raise ValidationError('That email address is already in use.')


class EditProject(FlaskForm):

    title = StringField('Title', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Description', validators=[
                            DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField('Save Project')