from api.models.__init__ import db
from sqlalchemy import distinct, or_
import logging


logger = logging.getLogger('api.models.books')

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
        results = [{'category': c[0]} for c in categories]
        return results
    except Exception as e:
        logger.error(f'error: {e}')
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
    

def check_db_connection():
    '''
    Executa uma consulta simples para verificar a conexão com o banco de dados.
    '''
    try:
        db.session.query(Books).limit(1).all()
        return True
    except Exception as e:
        logger.error(f'error: {e}')
        return False
    

def get_book_by_upc(upc):
    '''
    Retorna todos os detalhes de um livro com base no seu UPC.
    '''
    try:
        book = db.session.query(Books).filter_by(upc=upc).first()
        if book:
            result = {
                'upc': book.upc,
                'title': book.title,
                'genre': book.genre,
                'price': book.price,
                'availability': book.availability,
                'rating': book.rating,
                'description': book.description,
                'product_type': book.product_type,
                'price_excl_tax': book.price_excl_tax,
                'price_incl_tax': book.price_incl_tax,
                'tax': book.tax,
                'number_of_reviews': book.number_of_reviews,
                'url': book.url
            }
            return result
        return None
    except Exception as e:
        logger.error(f'error: {e}')
        return None
    

def get_books_by_title_or_category(title=None, genre=None):
    '''
    Busca livros por título OU categoria.
    '''
    try:
        filters = []
        if title:
            filters.append(Books.title.ilike(f'%{title}%'))
        if genre:
            filters.append(Books.genre.ilike(f'%{genre}%'))
        if filters:
            query = db.session.query(Books).filter(or_(*filters))
        else:
            return [] 
        books = query.order_by(Books.title.asc()).all()
        results = []
        for book in books:
            results.append({
                'upc': book.upc,
                'title': book.title,
                'genre': book.genre,
                'price': book.price
            })
        return results
    except Exception as e:
        logger.error(f'error: {e}')
        return None