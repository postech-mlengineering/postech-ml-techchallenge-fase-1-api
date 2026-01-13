import logging
from flask import Blueprint, jsonify
from api.models.books import Books
from api.extensions import db
from sqlalchemy import text 
from api.scripts.scrape_utils import run_scraping
from flask_jwt_extended import jwt_required


logger = logging.getLogger(__name__)
scrape_bp = Blueprint('scrape', __name__)


@scrape_bp.route('/', methods=['POST'])
@jwt_required()
def scrape():
    '''
    Realiza o web scraping para aquisição dos dados
    ---
    tags:
        - Scrape 
    summary: Web scraping.
    description: |
        Endpoint responsável pelo processo de web scraping e inserção de novos registros na tabela books.
    responses:
        200:
            description: Web scraping.
            schema:
                type: object
                properties:
                    msg:
                        type: string
                        description: Mensagem de sucesso do web scraping.
                    total_records:
                        type: integer
                        description: Número de registros inseridos.
            examples:
                application/json:
                    - msg: 'Web scraping realizado com sucesso'
                    - total_records: 1000
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
        logger.info('Iniciando scraping no Postgres...')
        df_books = run_scraping()

        if df_books is None or df_books.empty:
            return jsonify({'msg': 'Nenhum dado coletado.'}), 200
        
        truncate_sql = text(f'TRUNCATE TABLE {Books.__tablename__} RESTART IDENTITY CASCADE;')
        
        db.session.execute(truncate_sql)
        data_to_insert = df_books.to_dict(orient='records') 
        db.session.bulk_insert_mappings(Books, data_to_insert)

        db.session.commit()

        return jsonify({
            'msg': 'Web scraping realizado com sucesso',
            'total_records': len(data_to_insert)
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f'error: {e}')
        return jsonify({'error': str(e)}), 500