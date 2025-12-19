import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, get_jwt_identity, 
    jwt_required, create_refresh_token
)
from flask_bcrypt import Bcrypt
from api.models.user import db, User
from api.models.users_access import UserAccess
from api.models.refresh_token_manager import RefreshTokenManager
from datetime import datetime
from api.scripts.auth_utils import get_user_by_username
from api.config.config import Config


bcrypt = Bcrypt()
logger = logging.getLogger('api.routes.auth')
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register_user():
    '''
    Registra um novo usuário
    ---
    tags:
      - Auth
    summary: Registro de usuário.
    description: |
        Endpoint responsável por registrar usuário.
    parameters:
        - in: body
          name: body
          required: true
          schema:
            type: object
            properties:
                username:
                    type: string
                    example: 'hugo'
                password:
                    type: string
                    example: '123456'
    responses:
        201:
            description: Usuário criado com sucesso.
            schema:
                type: object
                properties:
                    msg:
                        type: string
                        description: Mensagem de succeso para registro de usuário.
            examples:
                application/json:
                    msg: 'Usuário criado com sucesso'
        400:
            description: Usuário já existe.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro para registro de usuário.
            examples:
                application/json:
                    error: 'Usuário já existe'
        500:
            description: Erro interno do servidor.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro interno do servidor.
            examples:
                application/json:
                    error: '<erro interno do servidor>'
    '''
    data = request.get_json(force=True)

    if get_user_by_username(data['username']):
        return jsonify({'error': 'Usuário já existe'}), 400
    try:
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(username=data['username'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f'error: {e}')
        return jsonify({'error': e}), 500
    
    return jsonify({'msg': 'Usuário criado com sucesso'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    '''
    Realiza a autenticação do usuário e gera tokens JWT
    ---
    tags:
      - Auth
    summary: Autenticação de usuário e geração de tokens.
    description: |
        Endpoint responsável por autenticar o usuário.
        Caso as credenciais estejam corretas, o endpoint:
            - Registra o acesso do usuário na tabela `user_access`
            - Verifica se já existe um *refresh token* válido no banco
            - Caso exista, reutiliza o *refresh token* e gera um novo *access token*
            - Caso não exista, cria um novo *refresh token* e salva no banco
            - Retorna *access token* e *refresh token`*
        O *access token* é curto (ex.: 15 minutos), enquanto o *refresh token* é válido por mais tempo (ex.: 1 dia), sendo reaproveitado até expirar.
    parameters:
        - in: body
          name: body
          required: true
          schema:
              type: object
              properties:
                  username:
                      type: string
                      example: 'hugo'
                  password:
                      type: string
                      example: '123456'
              required:
                  - username
                  - password
    responses:
        200:
            description: Autenticação realizada com sucesso.
            schema:
                type: object
                properties:
                    msg:
                        type: string
                        description: Mensagem de sucesso para autenticação do usuário.
            examples:
                application/json:
                    access_token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
                    refresh_token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
        401:
            description: Usuário ou senha inválidas.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro para login de usuário.
            examples:
                application/json:
                    error: 'Usuário ou senha inválidas'

    returns:
        JSON: Tokens JWT ou mensagem de erro.
    '''
    data = request.get_json(force=True)
    user = get_user_by_username(data['username'])

    if not user:
        return jsonify({'error': 'Usuário ou senha inválidas'}), 401
    
    if user and bcrypt.check_password_hash(user.password, data['password']):

        new_login = UserAccess(username=data['username'], created_at = datetime.utcnow())

        db.session.add(new_login)
        db.session.commit()
            
        existing_refresh_token = (
            RefreshTokenManager.query.filter(
                    RefreshTokenManager.username == user.username,
                    RefreshTokenManager.refresh_token_expire_at > datetime.utcnow()
                ).order_by(RefreshTokenManager.created_at.desc()).first()
            )
        
        if existing_refresh_token:
            access_token    = create_access_token(identity=str(user.id))
            return jsonify({
                'access_token': access_token,
                'refresh_token': existing_refresh_token.refresh_token
            }), 200
        
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        new_refresh_token_to_db = RefreshTokenManager(
            username=data['username'],
            refresh_token = refresh_token,
            refresh_token_expire_at = datetime.utcnow() + Config.JWT_REFRESH_TOKEN_EXPIRES
        )
        db.session.add(new_refresh_token_to_db)
        db.session.commit()

        return jsonify({
            'access_token': access_token, 
            'refresh_token': refresh_token
        }), 200
        
    return jsonify({'error': 'Usuário ou senha inválidas'}), 401


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    '''
    Atualiza token de acesso
    ---
    tags:
        - Auth
    summary: Atualização do token de acesso.
    description: |
        Endpoint utilizado para gerar um novo *access token* a partir de um *refresh token* válido.
        
        O *refresh token* deve ser enviado no header `Authorization` usando o formato: `Bearer <refresh_token>`.
    responses:
        200:
            description: Novo access token gerado com sucesso.
            schema:
                type: object
                properties:
                    msg:
                        type: string
                        description: Mensagem de sucesso para atualização do token.
            examples:
                application/json:
                    'access token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
        401:
            description: Erro de autenticação JWT.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro de autenticação.
            examples:
                application/json:
                    error: 'Erro de autenticação'
        500:
            description: Erro interno do servidor.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro interno do servidor.
            examples:
                application/json:
                    error: '<erro interno do servidor>'
    '''
    try:
        identity = get_jwt_identity()
        user_access = RefreshTokenManager.query.filter_by(
            refresh_token=request.headers.get('Authorization').replace('Bearer ', '')
        ).first()

        if not user_access:
            return jsonify({'error': 'Refresh token inválido ou não existe, fazer o Login novamente'}), 401
        if datetime.utcnow() > user_access.refresh_token_expire_at:
            return jsonify({'error': 'Refresh token expirado, fazer login novamente'}), 401
        
        new_acess_token = create_access_token(identity=identity)

        return jsonify({'access token': new_acess_token}), 200
    
    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': e}), 500
