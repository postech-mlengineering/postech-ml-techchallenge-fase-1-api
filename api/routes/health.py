from flask import Blueprint, jsonify
from api.models.__init__ import db


health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    '''
    Verificação de status e saúde da API.
    ---
    responses:
        200:
            description: A API está operacional e conectada ao BD.
            schema:
                type: object
                properties:
                    status:
                        type: string
                        example: up
                    database:
                        type: string
                        example: connected
        503:
            description: A API está no ar, mas um serviço crítico (BD) falhou.
            schema:
                type: object
                properties:
                    status:
                        type: string
                        example: down
                    database:
                        type: string
                        example: disconnected
    '''
    try:
        db.session.execute(db.select([1]))
        db_status = 'conectado'
        overall_status = 'up'
        status_code = 200
    except Exception:
        db_status = 'desconectado'
        overall_status = 'down'
        status_code = 503
    return jsonify({
        'status': overall_status,
        'database': db_status,
        'message': 'API funcionando corretamente' if overall_status == 'UP' else 'Critical service failure'
    }), status_code