from flask import render_template, redirect, url_for, session, flash
from app.auth import bp
from app.auth.decorators import login_required
from app.auth.forms import RegisterForm, LoginForm
from app.models import db, User


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id
        flash('Registration successful.')
        return redirect(url_for('main.index'))

    return render_template('auth/register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.')
            return redirect(url_for('auth.login'))

        session['user_id'] = user.id
        flash('Logged in successfully.')
        return redirect(url_for('main.index'))

    return render_template('auth/login.html', form=form)


@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out.')
    return redirect(url_for('main.index'))


@bp.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    return render_template('auth/profile.html', user=user)
