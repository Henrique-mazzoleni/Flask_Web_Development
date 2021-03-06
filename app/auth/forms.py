from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, Regexp, EqualTo, Email
from ..models import User


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1,64),
                                             Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1,64),
        Regexp('^[A-Za-z][A-Za-z0-9.]*$', 0,
        'Usernames must have only letters, numbers, dots or '
        'underscores.')])
    password = PasswordField('Password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')
    
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class ChangePassForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), EqualTo('confirm_pass', message='Passwords must match')])
    confirm_pass = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Request')


class ForgotenPassForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Reset')

    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValueError('There is no user registered with the given email.')

class ResetPassForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), EqualTo('confirm_pass', message='Passwords do not match.')])
    confirm_pass = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Change')

    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValueError('There is no user registered with the given email.')

class ChangeEmailForm(FlaskForm):
    new_email = StringField('New Email', validators=[DataRequired(), Length(1,64), Email()])
    submit = SubmitField('Send Confirmation')

    def validate_email(self, field):
        if User.query.filter_by(email=field.email.data).first():
            raise ValueError('There is already a user registered with this email adress.')