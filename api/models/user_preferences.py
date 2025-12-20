import logging
from datetime import datetime
from api.extensions import db


logger = logging.getLogger('__name__')


class UserPreferences(db.Model):
    '''Modelo de dados para a tabela user_preferences.'''
    __tablename__ = 'user_preferences'
    id                      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id                 = db.Column(db.Integer, nullable=True)
    inputed_book_id         = db.Column(db.Integer, nullable=True) 
    inputed_book_title      = db.Column(db.String(500), nullable=False) 
    recommended_book_id     = db.Column(db.Integer, nullable=False)
    recommended_book_title  = db.Column(db.String(500), nullable=False)
    similarity_score        = db.Column(db.Float, nullable=False)
    created_at              = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserPreferences: {self.inputed_book_title}, recommended: {self.recommended_book_id}>'