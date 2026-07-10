from app.auth import bp


@bp.route('/login')
def login():
    return 'Login'
