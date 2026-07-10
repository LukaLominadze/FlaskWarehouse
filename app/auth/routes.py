from flask import render_template, redirect, url_for, request, session, flash, jsonify
from app.auth import bp
from app.auth.decorators import login_required
from app.models import db, User


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not username or not email or not password:
            flash('All fields are required.')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('Username already taken.')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered.')
            return redirect(url_for('auth.register'))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id
        return redirect(url_for('main.index'))

    return render_template('auth/register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            flash('Invalid username or password.')
            return redirect(url_for('auth.login'))

        session['user_id'] = user.id
        return redirect(url_for('main.index'))

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main.index'))


@bp.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    return render_template('auth/profile.html', user=user)
