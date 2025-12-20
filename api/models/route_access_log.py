import logging
from datetime import datetime
from api.extensions import db


logger = logging.getLogger('__name__')


class RouteAccessLog(db.Model):
    '''Modelo de dados para a tabela route_access_log'''
    __tablename__ = 'route_access_log'
    id                  = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username            = db.Column(db.String(80), nullable=True)
    user_id             = db.Column(db.Integer, nullable=True)
    route               = db.Column(db.String(300), nullable=False)
    method              = db.Column(db.String(10), nullable=False)
    endpoint            = db.Column(db.String(150), nullable=True)
    route_blueprint     = db.Column(db.String(150), nullable=True)
    query_params        = db.Column(db.JSON, nullable=True)
    request_body        = db.Column(db.JSON, nullable=True)
    ip_address          = db.Column(db.String(100), nullable=True)
    user_agent          = db.Column(db.String(300), nullable=True)
    user_agent_browser  = db.Column(db.String(300), nullable=True)
    user_agent_platform = db.Column(db.String(100), nullable=True)
    created_at          = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Username {self.username}'