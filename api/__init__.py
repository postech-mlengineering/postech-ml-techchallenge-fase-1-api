import logging
from flask import Flask, jsonify
from sqlalchemy import inspect
#extensões
from api.extensions import db, jwt, swagger, bcrypt, cache, migrate
#configurações
from api.config import Config, TestingConfig
#blueprints
from api.routes.auth import auth_bp
from api.routes.health import health_bp
from api.routes.genres import genres_bp
from api.routes.books import books_bp
from api.routes.stats import stats_bp
from api.routes.scrape import scrape_bp
from api.routes.ml import ml_bp

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from api.logs import register_access_log


logger = logging.getLogger(__name__)


def register_jwt_handlers(jwt_manager):
    '''Encapsula os loaders de erro do JWT'''
    @jwt_manager.unauthorized_loader
    def unauthorized_callback(callback):
        return jsonify({'error': 'Token não informado ou cabeçalho ausente'}), 401

    @jwt_manager.invalid_token_loader
    def invalid_token_callback(err):
        logger.error(f'Token inválido: {err}')
        return jsonify({'error': 'Token inválido'}), 401

    @jwt_manager.expired_token_loader
    def expired_token_callback(header, payload):
        return jsonify({'error': 'Token expirado'}), 401
    

def create_app(testing=False):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('api')
    
    app = Flask(__name__)

    if testing:
        app.config.from_object(TestingConfig) #quando for teste usar o sqlite em memoria
    else:
        app.config.from_object(Config)

    #inicializa as extensões
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    swagger.init_app(app)
    bcrypt.init_app(app)
    cache.init_app(app)

    #tratamento de erros do JWT
    register_jwt_handlers(jwt)
    
    #registro de  requisições
    register_access_log(app)

    #registro de blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(health_bp, url_prefix='/api/v1/health')
    app.register_blueprint(genres_bp, url_prefix='/api/v1/genres')
    app.register_blueprint(books_bp, url_prefix='/api/v1/books')
    app.register_blueprint(stats_bp, url_prefix='/api/v1/stats')
    app.register_blueprint(scrape_bp, url_prefix='/api/v1/scrape')
    app.register_blueprint(ml_bp, url_prefix='/api/v1/ml')

    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["60 per minute"]
    )

    #rota raiz
    
    @app.route('/')
    #@limiter.limit('1 per minute')
    def home():
        return jsonify({
            'status': 'online',
            'msg': 'Bem-vindo à API.' 
        })
  
    #criação das tabelas do db
    with app.app_context():
        try: 
            logger.info(f'Tabelas do banco de dados criadas/verificadas. {inspect(db.engine).get_table_names()}')
        except Exception as e:
            logger.error('Erro crítico ao criar as tabelas do BD: %s', e)

    return app