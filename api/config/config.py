import os


class Config(object):
    '''Configuração da API'''
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///bookstoscrape.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'MEUSEGREDOAQUI')
    JWT_ALGORITHM = 'HS256'
    SWAGGER = {
        'title': 'API Flask',
        'uiversion': 3,
        'description': 'API Flask.'
    }