from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from . import auth
from ..models import User
from ..email import send_email
from .froms import LoginForm, RegistrationForm, ChangePassForm, ForgotenPassForm, ResetPassForm
from .. import db

@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():  
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html', user=current_user)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email = form.email.data,
                    username = form.username.data,
                    password = form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account', 
                    'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent. Please follow the link to confirm your email.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('main.index'))

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have successfully confirmed your email')
    else:
        flash('The confirmation link is invalid or expired')
    return redirect(url_for('main.index'))

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confrim Your Account','auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent.')
    return redirect(url_for('main.index'))

@auth.route('/changepass', methods=['GET', 'POST'])
@login_required
def change_password():
    if not current_user.confirmed:
        return redirect(url_for('auth.unconfirmed'))
    form = ChangePassForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            flash('You have successfully changed your password')
        else:
            flash('The current password provided is not valid')
        return redirect(url_for('main.index'))
    return render_template('/auth/changepass.html', form=form)

@auth.route('/forgotenpass', methods=['GET', 'POST'])
def forgoten_password():
    form = ForgotenPassForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        token = user.generate_confirmation_token()
        send_email(form.email.data, 'Password Reset', 'auth/email/forgotenpass', token=token, user=user)
        flash('An email has been sent to your registered email account.  Just follow the link to reset your password.')
        return redirect(url_for('main.index'))
    return render_template('/auth/forgotenpass.html', form=form)

@auth.route('/resetpass/<token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ResetPassForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user.confirm(token):
            user.password = form.new_password.data
            db.session.add(user)
            db.session.commit()
            flash('Your password was successfully reset.')
        else:
            flash('The token provided is not valid or expired. Please get a new token.')
        return redirect(url_for('auth.login'))
    return render_template('/auth/resetpass.html', form=form)