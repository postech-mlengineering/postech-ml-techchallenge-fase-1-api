import os
from datetime import timedelta


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

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=1)   # expiração do access token
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=10)     # expiração do refresh token
