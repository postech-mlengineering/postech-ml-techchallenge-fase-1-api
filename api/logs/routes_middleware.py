from flask import request, g
from api.models.__init__ import db
from api.models.route_access_log import RouteAccessLog
from api.models.user import User
import jwt

from api.config.config import Config


def get_user_from_token():
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None

    token = parts[1]
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=Config.JWT_ALGORITHM)
        user_id = payload.get('sub')  # pega o username do payload

        print(payload)
        
        if not user_id:
            return None

        # opcional: buscar o usuário completo no banco
        user = User.query.filter_by(id=user_id).with_entities(User.username).first() # Trazendo somente o username
        print(user)
        return user[0]

    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def register_route_logger(app):


    @app.before_request
    def log_request_info():
        ignored_routes = [
            '/favicon.ico',
            '/static',
            '/api/v1/auth/login',
            '/api/v1/auth/refresh'
        ]

        if any(request.path.startswith(r) for r in ignored_routes):
            return

        body = request.get_json(silent=True)
        ua = request.user_agent

        log = RouteAccessLog(
            username= get_user_from_token(),
            user_id=getattr(g, 'current_user_id', None),

            route=request.path,
            method=request.method,
            endpoint=request.endpoint,
            route_blueprint=request.blueprint,

            query_params=request.args.to_dict(),
            request_body=body,

            ip_address=request.headers.get('X-Forwarded-For', request.remote_addr),
            user_agent=str(ua),
            user_agent_browser=ua.browser,
            user_agent_platform=ua.platform,
        )

        db.session.add(log)
        db.session.commit()
