import logging
from datetime import datetime
from api.models.__init__ import db


logger = logging.getLogger('api.models.book_recommendation')


class BookRecommendation(db.Model):
    '''Modelo de dados para a tabela book_recommendation.'''
    __tablename__ = 'book_recommendation'
    id                      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id                 = db.Column(db.Integer, nullable=True)  # ID do usuário que solicitou a recomendação
    original_book_id        = db.Column(db.Integer, nullable=True)  # ID do livro original (opcional)
    original_title          = db.Column(db.String(500), nullable=False)  # Título do livro original
    recommended_book_id    = db.Column(db.Integer, nullable=False)  # ID do livro recomendado
    similarity_score       = db.Column(db.Float, nullable=False)  # Score de similaridade
    created_at             = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<BookRecommendation original: {self.original_title}, recommended: {self.recommended_book_id}>'