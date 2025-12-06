import logging
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from sqlalchemy import inspect
from flask_bcrypt import Bcrypt

from api.config.config import Config
from api.routes.auth import auth_bp
from api.routes.health import health_bp
from api.routes.categories import categories_bp
from api.routes.books import books_bp
from api.routes.stats import stats_bp

from api.models.__init__ import db

from api.logs.routes_middleware import register_route_logger



bcrypt = Bcrypt()
logger = logging.getLogger('api.auth')

def create_app():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('api')
    
    app = Flask(__name__)
    app.config.from_object(Config)


    #inicializa as extensões com o app
    db.init_app(app)
    jwt = JWTManager(app)
    swagger = Swagger(app)
    bcrypt.init_app(app) #inicialização da instância de bcrypt que está no auth.py

    #tratamento de erros do JWT
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        if 'Missing' in str(callback) or 'Authorization header' in str(callback):
            return jsonify({'msg': 'Token não informado'}), 401
        return jsonify({'error': 'Erro de autenticação'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(err):
        logger.error(f'Erro de token inválido: {err}')
        return jsonify({'error': 'Token inválido'}), 401

    @jwt.expired_token_loader
    def expired_token_callback(header, payload):
        return jsonify({'error': 'Token expirado'}), 401

    #registro de blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(health_bp, url_prefix='/api/v1')
    app.register_blueprint(categories_bp, url_prefix='/api/v1')
    app.register_blueprint(books_bp, url_prefix='/api/v1/books')
    app.register_blueprint(stats_bp, url_prefix='/api/v1/stats')

    #Registrar todaas as requisições feitas
    register_route_logger(app)

    #rota raiz
    @app.route('/')
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