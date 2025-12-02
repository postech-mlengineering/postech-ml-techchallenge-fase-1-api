import logging
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from api.models.books import get_stats_overview, get_stats_by_category


logger = logging.getLogger('api.routes.stats')
stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/overview', methods=['GET'])
@jwt_required()
def stats_overview():
    '''
    Retorna estatísticas gerais da coleção.
    ---
    tags:
      - Estatísticas
    responses:
      200:
        description: Estatísticas gerais (total, preço médio, ratings).
    '''
    try:
        stats = get_stats_overview()
        if stats:
            return jsonify(stats), 200
        return jsonify({'msg': 'Nenhuma estatística disponível'}), 404
    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': e}), 500


@stats_bp.route('/categories', methods=['GET'])
@jwt_required()
def stats_categories():
    '''
    Retorna estatísticas detalhadas por categoria.
    ---
    tags:
      - Estatísticas
    responses:
      200:
        description: Estatísticas detalhadas por categoria (quantidade, preço médio).
    '''
    try:
        stats = get_stats_by_category()
        if stats:
            return jsonify(stats), 200
        return jsonify({'msg': 'Nenhuma estatística de categoria disponível'}), 404
    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': e}), 500