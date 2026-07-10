from functools import wraps
from flask import session, redirect, url_for, request, jsonify


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
                return jsonify({'error': 'unauthorized'}), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
