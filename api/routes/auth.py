import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from flask_bcrypt import Bcrypt
from api.models.user import db, User, get_user_by_username


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
    Gera um token JWT para autenticação.
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
        200:
            description: Login bem sucedido, retorna o token JWT
            schema:
                type: object
                properties:
                    access_token:
                        type: string
                        description: O token de acesso JWT
        401:
            description: Credenciais inválidas
    '''
    
    data = request.get_json(force=True)
    user = get_user_by_username(data['username'])
    
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({'access_token': access_token}), 200
    return jsonify({'error': 'Credenciais inválidas'}), 401