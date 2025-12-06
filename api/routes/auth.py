import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, get_jwt_identity
    , jwt_required, create_refresh_token)
from flask_bcrypt import Bcrypt
from api.models.user import db, User, get_user_by_username
from api.models.users_access import UserAccess
from api.models.refresh_token_manager import RefreshTokenManager
from datetime import datetime, timedelta




bcrypt = Bcrypt()
logger = logging.getLogger('api.routes.auth')
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register_user():
    '''
    Registra um novo usuário.
    ---
    parameters:
        - in: body
          name: body
          required: true
          schema:
            type: object
            properties:
                username:
                    type: string
                password:
                    type: string
    responses:
        201:
            description: Usuário criado com sucesso
        400:
            description: Usuário já existe
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
    Realiza login do usuário e gera tokens JWT.

    ---
    tags:
      - Autenticação
    summary: Realiza login e retorna tokens JWT
    description: >
        Endpoint responsável por autenticar um usuário a partir de **username** e **password**.  
        Caso as credenciais estejam corretas, o endpoint retorna:
        - Um **access token** válido por curto período  
        - Um **refresh token** válido por 1 dia  
        
        Se já existir um refresh token ainda válido no banco, ele será reutilizado, evitando gerar múltiplos tokens simultâneos para o mesmo usuário.
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        description: Credenciais do usuário.
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: "johndoe"
            password:
              type: string
              example: "my_password"
    responses:
      200:
        description: Login bem-sucedido.
        schema:
          type: object
          properties:
            access_token:
              type: string
              description: Token JWT de acesso de curta duração.
            refresh_token:
              type: string
              description: Token JWT usado para renovar o token de acesso.
      401:
        description: Credenciais inválidas.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Usuário ou senha inválidas"
    '''
    
    data = request.get_json(force=True)
    user = get_user_by_username(data['username'])

    if not user:
        return jsonify({'error': 'Usuário ou senha inválidas'}), 401
    
    
    if user and bcrypt.check_password_hash(user.password, data['password']):

      new_login = UserAccess(
            username=data['username'],
            created_at = datetime.utcnow()
        )
        
      db.session.add(new_login)
      db.session.commit()
        
      existing_refresh_token = (RefreshTokenManager.query
                              .filter(
                                  RefreshTokenManager.username == user.username,
                                  RefreshTokenManager.refresh_token_expire_at > datetime.utcnow()
                                  )
                                  .order_by(RefreshTokenManager.created_at.desc())
                                  .first()
                                  )
        
      if existing_refresh_token:
            # Usar o token que ainda está em vigor
            access_token    = create_access_token(identity=str(user.id))

            return jsonify({
                "acess_token": access_token,
                "refresh_token": existing_refresh_token.refresh_token}), 200

      access_token    = create_access_token(identity=str(user.id))
      refresh_token   = create_refresh_token(identity=str(user.id))

      new_refresh_token_to_db = RefreshTokenManager(username=data['username']
                                , refresh_token = refresh_token
                                , refresh_token_expire_at = datetime.utcnow() + timedelta(days=1) #Verificar com o Config

                                )
        
      db.session.add(new_refresh_token_to_db)
      db.session.commit()

      return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token}), 200
    
    return jsonify({'error': 'Usuário ou senha inválidas'}), 401


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh Access Token
    ---
    description: >
        Endpoint utilizado para gerar um novo *access token* a partir de um *refresh token* válido.
        O refresh token deve ser enviado no header `Authorization` usando o formato:
        `Bearer <refresh_token>`.

    tags:
      - Authentication

    responses:
      200:
        description: Novo access token gerado com sucesso.
        examples:
          application/json:
            {
              "Token refreshed": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
      401:
        description: Refresh token inválido, expirado ou ausente.
        examples:
          application/json:
            {
              "msg": "Token has expired"
            }
      500:
        description: Erro interno ao tentar renovar o token.
        examples:
          application/json:
            {
              "error": "Descrição do erro"
            }
    """
    try:
        
        identity = get_jwt_identity()
        
        user_access = RefreshTokenManager.query.filter_by(
            refresh_token=request.headers.get("Authorization").replace("Bearer ", "")
        ).first()

        if not user_access:
            return jsonify({"error": "Refresh token inválido ou não existe, fazer o Login novamente"}), 401

        if datetime.utcnow() > user_access.refresh_token_expire_at:
            return jsonify({"error": "Refresh token expirado, fazer login novamente"}), 401

        new_acess_token = create_access_token(identity=identity)

        return jsonify({"Token refreshed": new_acess_token}), 200
    
    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': e}), 500
