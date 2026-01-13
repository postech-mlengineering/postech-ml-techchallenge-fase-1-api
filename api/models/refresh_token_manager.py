import logging
from datetime import datetime
from api.extensions import db


logger = logging.getLogger(__name__)


class RefreshTokenManager(db.Model):
    '''Modelo de dados para a tabela refresh_token_manager.'''
    __tablename__ = 'refresh_token_manager'
    id                      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username                = db.Column(db.String(80), nullable=False)
    refresh_token           = db.Column(db.Text, nullable=True)
    created_at              = db.Column(db.DateTime, default=datetime.utcnow)
    refresh_token_expire_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Username {self.username}'