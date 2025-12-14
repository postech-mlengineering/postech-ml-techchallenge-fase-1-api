import logging
from sqlalchemy import distinct, or_, case
from api.models.books import Books


logger = logging.getLogger('api.scripts.books_utils')


def get_all_categories():
    '''
    Retorna todas as categorias (gêneros) de livros únicas disponíveis no banco de dados.

    Return:
        list: Uma lista de dicionários, onde cada dicionário contém a chave 'category'.
              Exemplo: [{'category': 'Travel'}, {'category': 'Mystery'}].
              Retorna None em caso de erro.
    '''
    try:
        categories = (
            Books.query.with_entities(distinct(Books.genre)).order_by(Books.genre.asc()).all()
        )
        results = [{'category': c[0]} for c in categories]
        return results
    except Exception as e:
        logger.error(f'error: {e}')
        return None


def get_all_book_titles():
    '''
    Retorna todos os títulos de livros únicos disponíveis no banco de dados.

    Return:
        list: Uma lista de dicionários, onde cada dicionário contém a chave 'book' (título).
              Exemplo: [{'book': 'A Light in the Attic'}, {'book': 'Tipping the Velvet'}].
              Retorna None em caso de erro.
    '''
    try:
        titles = (
            Books.query.with_entities(distinct(Books.title)).order_by(Books.title.asc()).all()
        )
        results = [{'title': c[0]} for c in titles]
        return results
    except Exception as e:
        print(f'Erro ao buscar livros: {e}')
        return None
    

def get_book_by_id(id):
    '''
    Retorna todos os detalhes de um livro com base no seu ID.

    Args:
        id (int): O ID único do livro no banco de dados.

    Return:
        dict: Um dicionário contendo todos os detalhes do livro, ou None se não for encontrado ou em caso de erro.
    '''
    try:
        book = Books.query.filter_by(id=id).first()
        if book:
            result = {
                'id': book.id,
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
                'url': book.url,
                'image_url': book.image_url
            }
            return result
        return None
    except Exception as e:
        logger.error(f'error: {e}')
        return None
    

def get_books_by_title_or_category(title=None, genre=None):
    '''
    Busca livros por título OU categoria (gênero), usando correspondência parcial (LIKE).

    Args:
        title (str, optional): O título ou parte do título a ser buscado. Padrão é None.
        genre (str, optional): A categoria (gênero) ou parte da categoria a ser buscada. Padrão é None.

    Return:
        list: Uma lista de dicionários contendo ID, UPC, título, gênero, preço e URL da imagem.
              Retorna uma lista vazia se nenhum filtro for fornecido. Retorna None em caso de erro.
    '''
    try:
        filters = []
        if title:
            filters.append(Books.title.ilike(f'%{title}%'))
        if genre:
            filters.append(Books.genre.ilike(f'%{genre}%'))
        if filters:
            query = Books.query.filter(or_(*filters))
        else:
            return [] 
        books = query.order_by(Books.title.asc()).all()
        results = []
        for book in books:
            results.append({
                'id': book.id,
                'upc': book.upc,
                'title': book.title,
                'genre': book.genre,
                'price': book.price,
                'image_url': book.image_url
            })
        return results
    except Exception as e:
        logger.error(f'error: {e}')
        return None


def get_books_by_price_range(min_price, max_price):
    '''
    Filtra livros dentro de uma faixa de preço específica (inclusiva).

    Args:
        min_price (float): O preço mínimo do livro.
        max_price (float): O preço máximo do livro.

    Return:
        list: Uma lista de dicionários contendo ID, UPC, título, gênero, preço e URL da imagem.
              Retorna None em caso de erro.
    '''
    try:
        books = (
            Books.query
            .filter(Books.price >= min_price, Books.price <= max_price)
            .order_by(Books.price.asc())
            .all()
        )
        results = []
        for book in books:
            results.append({
                'id': book.id,
                'upc': book.upc,
                'title': book.title,
                'genre': book.genre,
                'price': book.price,
                'image_url': book.image_url
            })
        return results
    except Exception as e:
        logger.error(f'error: {e}')
        return None
    

def get_top_rated_books(limit=10):
    '''
    Retorna os livros com a melhor avaliação (rating mais alto), convertendo ratings de texto para numérico.

    Args:
        limit (int, optional): O número máximo de livros a serem retornados. Padrão é 10.

    Return:
        list: Uma lista de dicionários contendo ID, UPC, título, gênero, rating, preço e URL da imagem.
              Retorna None em caso de erro.
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
            Books.query.add_columns(rating_case)
            .order_by(rating_case.desc(), Books.title.asc())
            .limit(limit)
            .all()
        )
        results = []
        for book, rating_val in top_books:
            results.append({
                'id': book.id,
                'upc': book.upc,
                'title': book.title,
                'genre': book.genre,
                'rating': book.rating,
                'price': book.price,
                'image_url': book.image_url
            })
        return results
    except Exception as e:
        logger.error(f'error: {e}')
        return None