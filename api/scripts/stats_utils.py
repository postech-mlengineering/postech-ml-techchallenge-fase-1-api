import logging
from sqlalchemy import func
from api.models.books import Books


logger = logging.getLogger('__name__')


def get_stats_overview():
    '''
    Calcula e retorna estatísticas agregadas globais do conjunto de livros.

    Calculates:
        - O número total de livros.
        - O preço médio de todos os livros.
        - A distribuição e contagem de cada nível de rating (avaliação).

    Returns:
        dict: Um dicionário contendo o total de livros, preço médio formatado e a distribuição de ratings.
              Retorna None em caso de erro.
    '''
    try:
        total_books = Books.query.count()
        avg_price = (
            Books.query
            .with_entities(func.avg(Books.price))
            .scalar()
        )
        rating_distribution = (
            Books.query.with_entities(Books.rating, func.count(Books.rating))
            .group_by(Books.rating)
            .order_by(func.count(Books.rating).desc())
            .all()
        )
        return {
            'total_books': total_books,
            'avg_price': round(avg_price, 2) if avg_price else 0.0,
            'rating_distribution': [{'rating': r[0], 'total': r[1]} for r in rating_distribution]
        }
    except Exception as e:
        logger.error(f'error: {e}')
        return None


def get_stats_by_category():
    '''
    Calcula estatísticas agregadas por categoria de livro.

    Calculates:
        - A quantidade de livros em cada categoria.
        - O preço médio dos livros em cada categoria.

    Returns:
        list: Uma lista de dicionários, onde cada dicionário contém a categoria, a quantidade de livros e o preço médio formatado.
              Retorna None em caso de erro.
    '''
    try:
        category_stats = (
            Books.query.with_entities(
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
                'category': stat.genre,
                'total': stat.count,
                'avg_price': round(stat.avg_price, 2)
            }
            for stat in category_stats
        ]
        return results
    except Exception as e:
        logger.error(f'error: {e}')
        return None