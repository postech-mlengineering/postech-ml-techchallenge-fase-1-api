import logging
from api.extensions import cache
from flask import Blueprint, jsonify
from api.scripts.genres_utils import get_all_genres
from flask_jwt_extended import jwt_required


logger = logging.getLogger('__name__')
genres_bp = Blueprint('genres', __name__)


@genres_bp.route('/genres', methods=['GET'])
@jwt_required()
@cache.cached(timeout=3600)
def genres():
    '''
    Retorna a lista de todas as categorias de livros.
    ---
    tags:
        - Genres
    summary: Listagem de categorias de livros.
    description: |
        Endpoint responsável por retornar lista com categorias de livros.
    responses:
        200:
            description: Lista de categorias de livros.
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
                    - category: 'Autobiography'
                    - category: 'Art'
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
        categorias = get_all_genres()
        if categorias:
            return jsonify(categorias), 200
        return jsonify({'msg': 'Sem categorias cadastradas'}), 200
    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': str(e)}), 500
