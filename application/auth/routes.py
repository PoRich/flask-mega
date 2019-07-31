# auth/routes.py
from flask import flash, render_template, redirect, request, url_for
from flask_login import current_user, login_user, logout_user
from flask_babel import _
from werkzeug.urls import url_parse
from application import db
from application.auth.forms import LoginForm, RegistrationForm,\
    ResetPasswordRequestForm, ResetPassword
from application.models import User
from application.auth.email import send_password_reset_email
from application.auth import bp

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        # sets this user to current_user
        next_page = request.args.get('next')
        # flask_login sets next keyword
        if not next_page or url_parse(next_page).netloc !='':
            # .netloc determines if the URL is relative or absolute
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title=_('Sign In'), form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        submitted_email = form.email.data
        user = User(username=form.username.data, email=submitted_email.lower())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Successfully Registered!'))
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title=_('Register'), form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        submitted_email = form.email.data
        user = User.query.filter_by(email=submitted_email.lower()).first()
        if user:
            send_password_reset_email(user)
            flash(_('Check your email for the instructions to reset your password'))
            return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title=_('Reset Password'), form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPassword()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
