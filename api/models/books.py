import logging
from api.models.__init__ import db


logger = logging.getLogger(__name__)


class Books(db.Model):
    '''Modelo de dados para a tabela books.'''
    __tablename__ = 'books'
    id                 = db.Column(db.Integer, primary_key=True, autoincrement=True)
    upc                = db.Column(db.String(50), nullable=False)
    title              = db.Column(db.String(500), nullable=False)
    genre              = db.Column(db.String(100), nullable=False)
    price              = db.Column(db.Float, nullable=False) 
    availability       = db.Column(db.Integer, nullable=False)
    rating             = db.Column(db.String(50), nullable=False)
    description        = db.Column(db.Text, nullable=False)
    product_type       = db.Column(db.String(50), nullable=False)
    price_excl_tax     = db.Column(db.Float, nullable=False)
    price_incl_tax     = db.Column(db.Float, nullable=False)
    tax                = db.Column(db.Float, nullable=False)
    number_of_reviews  = db.Column(db.Integer, nullable=False)
    url                = db.Column(db.String(1024), nullable=False)
    image_url          = db.Column(db.String(1024), nullable=False)
    
    def __repr__(self):
        return f'<Title {self.title}>'