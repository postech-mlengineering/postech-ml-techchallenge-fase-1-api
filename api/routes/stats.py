import logging
from api.extensions import cache
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from api.scripts.stats_utils import get_stats_overview, get_stats_by_category


logger = logging.getLogger('__name__')
stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/overview', methods=['GET'])
@jwt_required()
@cache.cached(timeout=3600)
def stats_overview():
    '''
    Retorna estatísticas gerais da coleção.
    ---
    tags:
        - Statistics
    summary: Estatísticas gerais da coleção.
    description: |
        Endpoint responsável por retornar estatísticas gerais da coleção.
    responses:
        200:
            description: Estatísticas gerais da coleção.
            schema:
                type: object
                properties:
                    avg_price:
                        type: number
                        format: float
                        description: Preço médio dos livros na coleção.
                    total_books:
                        type: integer
                        description: Número total de livros na coleção.
                    rating_distribution:
                        type: array
                        description: Distribuição de contagem de livros por avaliação (rating).
                        items:
                            type: object
                            properties:
                                total:
                                    type: integer
                                    description: Quantidade de livros com a avaliação especificada.
                                rating:
                                    type: string
                                    description:
            examples:
                application/json:
                    avg_price: 35.07
                    rating_distribution:
                        - total: 226
                          rating: 'One'
                        - total: 203
                          rating: 'Three'
                        - total: 196
                          rating: 'Two'
                        - total: 196
                          rating: 'Five'
                        - total: 179
                          rating: 'Four'
                    total_books: 1000
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
        stats = get_stats_overview()
        if stats:
            return jsonify(stats), 200
        return jsonify({'msg': 'Nenhuma estatística disponível'}), 404
    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': str(e)}), 500


@stats_bp.route('/categories', methods=['GET'])
@jwt_required()
@cache.cached(timeout=3600)
def stats_categories():
    '''
    Retorna estatísticas detalhadas por categoria.
    ---
    tags:
        - Statistics
    summary: Estatísticas gerais da coleção por categoria.
    description: |
        Endpoint responsável por retornar estatísticas detalhadas por categoria.
    responses:
        200:
              description: Estatísticas gerais da coleção por categoria.
              schema:
                type: array
                items:
                    type: object
                    properties:
                        avg_price: 
                            type: number
                            format: float
                            description: Média de preços.
                        category: 
                            type: string
                            description: Categoria ou gênero do livro.
                        total: 
                            type: number
                            format: integer
                            description: Total de livros na categoria.
              examples:
                  application/json:
                      - avg_price: 34.39
                        category: 'Default'
                        total: 152
                      - avg_price: 34.26
                        category: 'Nonfiction'
                        total: 110
                      - avg_price: 34.57
                        category: 'Sequential Art'
                        total: 75
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
        stats = get_stats_by_category()
        if stats:
            return jsonify(stats), 200
        return jsonify({'msg': 'Nenhuma estatística de categoria disponível'}), 404
    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': str(e)}), 500