from api.models.__init__ import db
from sqlalchemy import distinct, or_, case, func
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


def get_books_by_price_range(min_price, max_price):
    '''
    Filtra livros dentro de uma faixa de preço específica.
    '''
    try:
        books = (
            db.session.query(Books)
            .filter(Books.price >= min_price, Books.price <= max_price)
            .order_by(Books.price.asc())
            .all()
        )
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


def get_top_rated_books(limit=10):
    '''
    Retorna os livros com a melhor avaliação (rating mais alto).
    '''
    rating_map = {
        'One': 1, 
        'Two': 2, 
        'Three': 3, 
        'Four': 4, 
        'Five': 5
    }
    try:
        rating_case = case(rating_map, value=Books.rating).label('rating_value')
        top_books = (
            db.session.query(Books, rating_case)
            .order_by(rating_case.desc(), Books.title.asc())
            .limit(limit)
            .all()
        )
        results = []
        for book, rating_val in top_books:
            results.append({
                'upc': book.upc,
                'title': book.title,
                'genre': book.genre,
                'rating': book.rating,
                'price': book.price
            })
        return results
    except Exception as e:
        logger.error(f'error: {e}')
        return None
    

def get_stats_overview():
    '''
    Calcula o total de livros, preço médio e distribuição de ratings.
    '''
    try:
        total_books = db.session.query(Books).count()
        avg_price = db.session.query(func.avg(Books.price)).scalar()
        rating_distribution = (
            db.session.query(Books.rating, func.count(Books.rating))
            .group_by(Books.rating)
            .order_by(func.count(Books.rating).desc())
            .all()
        )
        return {
            'total_livros': total_books,
            'preco_medio': round(avg_price, 2) if avg_price else 0.0,
            'distribuicao_ratings': [{'rating': r[0], 'count': r[1]} for r in rating_distribution]
        }
    except Exception as e:
        logger.error(f'error: {e}')
        return None
    

def get_stats_by_category():
    '''
    Calcula a quantidade e o preço médio por categoria.
    '''
    try:
        category_stats = (
            db.session.query(
                Books.genre,
                func.count(Books.genre).label('count'),
                func.avg(Books.price).label('avg_price')
            )
            .group_by(Books.genre)
            .order_by(func.count(Books.genre).desc())
            .all()
        )
        results = [
            {
                'categoria': stat.genre,
                'quantidade': stat.count,
                'preco_medio': round(stat.avg_price, 2)
            }
            for stat in category_stats
        ]
        return results
    except Exception as e:
        logger.error(f'error: {e}')
        return None