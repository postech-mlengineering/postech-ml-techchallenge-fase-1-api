from flask import Blueprint, jsonify
import datetime
from api.models.books import check_db_connection
from api.models.__init__ import db


health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    '''
    Verifica o status da API, incluindo a conexão com o banco de dados.
    ---
    tags:
      - Saúde
    responses:
      200:
        description: A API está operacional, com ou sem conexão com o DB.
        schema:
          type: object
          properties:
            api_status:
              type: string
              description: Status da API (OK).
            db_status:
              type: string
              description: Status da conexão com o Banco de Dados (UP ou DOWN).
            timestamp:
              type: string
              description: Data e hora da verificação.
        examples:
          application/json: 
            api_status: OK
            db_status: UP
            timestamp: "2025-12-02T19:40:00.000000Z"
    '''

    db_connected = check_db_connection()
    db_status_str = 'UP' if db_connected else 'DOWN'

    response = {
        'api_status': 'OK',
        'db_status': db_status_str,
        'timestamp': datetime.datetime.now().isoformat()
    }
    return jsonify(response), 200
