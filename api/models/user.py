import datetime
from api.models.__init__ import db


class User(db.Model):
    '''Modelo de dados para a tabela de usuários.'''
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'
    

def get_user_by_username(username):
    user = User.query.filter_by(username=username).first()
    return user