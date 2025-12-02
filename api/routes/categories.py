import logging
from flask import Blueprint, jsonify
from flask_bcrypt import Bcrypt
from api.models.books import get_all_categories
from flask_jwt_extended import jwt_required


logger = logging.getLogger('api.routes.categories')
categories_bp = Blueprint('categories', __name__)


@categories_bp.route('/categories', methods=['GET'])
@jwt_required()
def categories():
    '''
    Retorna a lista de todas as categorias de livros.
    ---
    tags:
      - Categorias
    responses:
      200:
        description: Lista de categorias ou mensagem de que não há categorias.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                description: ID da categoria.
              nome:
                type: string
                description: Nome da categoria.
        examples:
          application/json: 
            - id: 1
              nome: Ficção Científica
            - id: 2
              nome: Romance
            - id: 3
              nome: Fantasia
      401:
        description: Erro interno ou de autenticação (se aplicável na exceção).
        schema:
          type: object
          properties:
            error:
              type: string
              description: Mensagem de erro.
    '''
    try:
        categorias = get_all_categories()
        if categorias:
            return jsonify(categorias), 200
        return jsonify({'msg': 'Sem categorias cadastradas'}), 200
    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': e}), 401
