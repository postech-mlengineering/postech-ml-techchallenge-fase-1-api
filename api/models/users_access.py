import logging
import datetime
from api.extensions import db


logger = logging.getLogger('__name__')


class UserAccess(db.Model):
    '''Modelo de dados para a tabela user_access.'''
    __tablename__ = 'user_access'
    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username   = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<Username {self.username}'