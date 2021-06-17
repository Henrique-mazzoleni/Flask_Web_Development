from flask import render_template, redirect, request, url_for, flash, current_app
from flask_login import login_user, login_required, logout_user, current_user

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from . import auth
from ..models import User
from ..email import send_email
from .froms import LoginForm, RegistrationForm, ChangePassForm, ForgotenPassForm, ResetPassForm, ChangeEmailForm
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

@auth.route('/accountconfirm/<token>')
@login_required
def account_confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.check_token(token):
        current_user.confirmed = True
        db.session.add(current_user)
        db.session.commit()
        flash('You have successfully confirmed your email')
    else:
        flash('The confirmation link is invalid or expired')
    return redirect(url_for('main.index'))

@auth.route('/emailconfirm/<token>')
@login_required
def email_confirm(token):
    if current_user.check_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except Exception:
            flash('Token invalid or expired. Please regenerate Token.')
            return redirect(url_for('main.index'))
        if data.get('email'):
            current_user.email = data.get('email')
            db.session.add(current_user)
            db.session.commit()
            flash('New email confirmed and saved.')
        else:
            flash('There was something wrong with the token provided. Please generate a new token.')
    else:
        flash('The token was invalid or expired. Please generate a new token.')
    return redirect(url_for('main.index'))


@auth.route('/accountconfirm')
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
        if user.check_token(token):
            user.password = form.new_password.data
            db.session.add(user)
            db.session.commit()
            flash('Your password was successfully reset.')
        else:
            flash('The token provided is not valid or expired. Please get a new token.')
        return redirect(url_for('auth.login'))
    return render_template('/auth/resetpass.html', form=form)

@auth.route('/changemail', methods=['GET', 'POST'])
@login_required
def change_email():
    if not current_user.confirmed:
        return redirect(url_for('auth.unconfirmed'))
    form = ChangeEmailForm()
    if form.validate_on_submit():
        token = current_user.generate_confirmation_token(email=form.new_email.data)
        send_email(form.new_email.data, 'Confirm New Email', 'auth/email/confirmnewemail', token=token, user=current_user)
        flash('An email has been sent to the new email adress. Please follow the link to confirm the new adress.')
        return redirect(url_for('main.index'))
    return render_template('/auth/changemail.html', form=form)