import logging
from flask import request
from api.extensions import db
from api.models.route_access_log import RouteAccessLog
from api.models.user import User
from flask_jwt_extended import decode_token


logger = logging.getLogger(__name__)


def get_user_info():
    '''Extrai informações do usuário'''
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None, None
    try:
        token = auth_header.split(" ")[1]
        data = decode_token(token)
        user_id = data.get('sub')
        user = db.session.query(User.username).filter(User.id == user_id).first()
        return user_id, (user.username if user else "Usuário não encontrado")
    except Exception as e:
        logger.error(f'error: {e}')
        return None, 'Token Inválido'


def register_route_logger(app):
    @app.before_request
    def log_request_info():
        #ignorando logs de rotas desnecessárias
        ignored_prefixes = ['/favicon.ico', '/static', '/api/v1/auth', '/flasgger', '/api/v1/health']
        if any(request.path.startswith(p) for p in ignored_prefixes):
            return

        user_id, username = get_user_info()
        try:
            log = RouteAccessLog(
                username=username,
                user_id=user_id,
                route=request.path,
                method=request.method,
                endpoint=request.endpoint,
                route_blueprint=request.blueprint,
                query_params=request.args.to_dict(),
                request_body=request.get_json(silent=True),
                ip_address=request.headers.get('X-Forwarded-For', request.remote_addr),
                user_agent=str(request.user_agent),
                user_agent_browser=request.user_agent.browser,
                user_agent_platform=request.user_agent.platform,
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f'error: {e}')