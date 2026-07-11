from functools import wraps
from flask import session, redirect, url_for, request, jsonify, flash


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
                return jsonify({'error': 'unauthorized'}), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
                return jsonify({'error': 'unauthorized'}), 401
            return redirect(url_for('auth.login'))
        from app.models import User
        user = User.query.get(session['user_id'])
        if user is None or not user.is_admin:
            flash('Admin access required.', 'danger')
            if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
                return jsonify({'error': 'forbidden'}), 403
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function
