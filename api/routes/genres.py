import logging
from api.extensions import cache
from flask import Blueprint, jsonify
from api.scripts.genres_utils import get_all_genres
from flask_jwt_extended import jwt_required


logger = logging.getLogger(__name__)
genres_bp = Blueprint('genres', __name__)


@genres_bp.route('/', methods=['GET'])
@jwt_required()
@cache.cached(timeout=3600)
def genres():
    '''
    Retorna lista com todos os gêneros de livros cadastrados
    ---
    tags:
        - Genres
    summary: Listagem de gêneros de livros cadastrados.
    description: |
        Endpoint responsável por retornar lista com gêneros de livros cadastrados.
    responses:
        200:
            description: Listagem de gêneros de livros cadastrados.
            schema:
                type: array
                items:
                  type: object
                  properties:
                      genre:
                          type: string
                          description: Nome do gênero.
            examples:
                application/json: 
                    - genre: 'Autobiography'
                    - genre: 'Art'
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
                    error: '<erro de autenticação>'
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
