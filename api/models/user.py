import logging
from datetime import datetime
from api.extensions import db


logger = logging.getLogger(__name__)


class User(db.Model):
    '''Modelo de dados para a tabela user.'''
    __tablename__ = 'user'
    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username   = db.Column(db.String(80), unique=True, nullable=False)
    password   = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'