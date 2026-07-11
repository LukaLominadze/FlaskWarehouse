from flask import Flask, render_template, jsonify, request
from flask_wtf.csrf import CSRFProtect
from config import Config
from app.models import db

csrf = CSRFProtect()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        from app import models
        db.create_all()

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    csrf.exempt(api_bp)

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    @app.context_processor
    def inject_user():
        from flask import session
        from app.models import User
        user = None
        if session.get('user_id'):
            user = User.query.get(session['user_id'])
        return dict(current_user=user)

    @app.errorhandler(404)
    def not_found(error):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'error': 'not found'}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'error': 'internal server error'}), 500
        return render_template('errors/500.html'), 500

    @app.cli.command('create-admin')
    def create_admin():
        """Create an admin user interactively."""
        import getpass
        username = input('Username: ').strip()
        if not username:
            print('Username cannot be empty.')
            return
        email = input('Email: ').strip()
        if not email:
            print('Email cannot be empty.')
            return
        existing = models.User.query.filter(
            db.or_(models.User.username == username, models.User.email == email)
        ).first()
        if existing:
            print(f'User with that username or email already exists (id={existing.id}).')
            return
        password = getpass.getpass('Password: ')
        if len(password) < 6:
            print('Password must be at least 6 characters.')
            return
        confirm = getpass.getpass('Confirm password: ')
        if password != confirm:
            print('Passwords do not match.')
            return
        user = models.User(username=username, email=email, is_admin=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f'Admin user "{username}" created (id={user.id}).')

    @app.cli.command('promote-user')
    def promote_user():
        """Promote an existing user to admin."""
        username = input('Username to promote: ').strip()
        user = models.User.query.filter_by(username=username).first()
        if not user:
            print(f'User "{username}" not found.')
            return
        if user.is_admin:
            print(f'"{username}" is already an admin.')
            return
        user.is_admin = True
        db.session.commit()
        print(f'"{username}" is now an admin.')

    return app
