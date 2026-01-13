import logging
from api.extensions import db
from api.models.access_log import AccessLog
from api.models.user import User
from flask import request, g
from flask_jwt_extended import decode_token
import time


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
        return user_id, (user.username if user else 'Usuário não encontrado')
    except Exception as e:
        logger.error(f'error: {e}')
        return None, 'Token Inválido'


def register_access_log(app):
    @app.before_request
    def start_timer():
        g.start_time = time.time()

    @app.after_request
    def log_enriched_info(response):
        ignored_prefixes = ['/favicon.ico', '/static', '/flasgger', '/api/v1/health']
        if any(request.path.startswith(p) for p in ignored_prefixes):
            return response
        duration_ms = 0
        if hasattr(g, 'start_time'):
            duration_ms = (time.time() - g.start_time) * 1000

        user_id, username = get_user_info()
        try:
            log_entry = AccessLog(
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
                response_time_ms=round(duration_ms, 2),
                status_code=response.status_code
            )
            db.session.add(log_entry)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f'Erro ao salvar log de rota: {e}')

        return response