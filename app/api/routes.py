from app.api import bp


@bp.route('/status')
def status():
    return {'status': 'ok'}
