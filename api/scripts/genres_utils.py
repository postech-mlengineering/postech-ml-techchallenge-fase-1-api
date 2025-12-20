import logging
from sqlalchemy import distinct
from api.models.books import Books


logger = logging.getLogger('__name__')


def get_all_genres():
    '''
    Retorna todas as categorias (gêneros) de livros únicas disponíveis no banco de dados.

    Retorna:
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