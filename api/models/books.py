import datetime
from api.models.__init__ import db
from sqlalchemy import distinct


class Books(db.Model):
    '''Modelo de dados para a tabela de Books.'''
    __tablename__ = 'books'
    upc             = db.Column(db.String(100), primary_key=True)
    title           = db.Column(db.String(120), nullable=False)
    genre           = db.Column(db.String(80), nullable=False)
    price           = db.Column(db.Float, nullable=False) 
    availability    = db.Column(db.Integer, nullable=False)
    rating          = db.Column(db.String(20), nullable=False)
    description     = db.Column(db.Text, nullable=False)
    product_type    = db.Column(db.String(15), nullable=False)
    price_excl_tax  = db.Column(db.Float, nullable=False)
    price_incl_tax   = db.Column(db.Float, nullable=False)
    tax             = db.Column(db.Float, nullable=False)
    number_of_reviews  = db.Column(db.Integer, nullable=False)
    url             = db.Column(db.String(200), nullable=False)
    def __repr__(self):
        return f'<Title {self.title}>'


def get_all_categories():
    try:
        categories = (
            db.session.query(distinct(Books.genre)).order_by(Books.genre.asc()).all()
        )
        results = [{'categories': c[0]} for c in categories]
        return results
    except Exception as e:
        print(f'Erro ao buscar categrias: {e}')
        return None
    
def get_all_books():
    try:
        books = (
            db.session.query(distinct(Books.title)).order_by(Books.title.asc()).all()
        )
        results = [{'book': c[0]} for c in books]
        return results
    except Exception as e:
        print(f'Erro ao buscar livros: {e}')
        return None