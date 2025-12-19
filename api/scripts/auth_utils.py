import logging
from api.models.user import User


logger = logging.getLogger('api.scripts.user_utils')


def get_user_by_username(username):
    '''
    Busca e retorna um objeto de usuário (User) baseado no nome de usuário (username).

    Args:
        username (str): O nome de usuário a ser buscado no banco de dados.

    Returns:
        User: O objeto User correspondente ao username, ou None se nenhum usuário for encontrado.
    '''
    user = User.query.filter_by(username=username).first()
    return user