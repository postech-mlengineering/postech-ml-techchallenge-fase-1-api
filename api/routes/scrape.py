import logging
from flask import Blueprint, jsonify
from api.models.books import Books
from api.models.__init__ import db
from sqlalchemy import text 
from api.scripts.scrape_utils import run_scraping_and_save_data


scrape_bp = Blueprint('scrape', __name__)
logger = logging.getLogger('api.routes.scrape')


@scrape_bp.route('/scrape', methods=['POST'])
def scrape():
    '''
    Executa o web scraping, salva CSV e insere novos registros na tabela books.
    ---
    tags:
        - scrape 
    summary: Web scraping e inserção de dados.
    description: |
        Endpoint responsável pelo processo de web scraping e inserção de novos registros na tabela books.
    responses:
        200:
            description: Dados de livros coletados e inseridos com sucesso.
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
                    - msg: 'Dados coletados, salvos em CSV e inseridos no banco de dados com sucesso'
                    - total_records: 1000
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
        logger.info('Iniciando o processo de scraping.')
        df_books = run_scraping_and_save_data()
        
        if df_books.empty:
            return jsonify({'msg': 'Scraping finalizado, mas nenhum dado foi coletado.'}), 200
        
        with db.session.begin():
            truncate_sql = f'TRUNCATE TABLE {Books.__tablename__} RESTART IDENTITY;'
            db.session.execute(text(truncate_sql)) 

            data_to_insert = df_books.to_dict(orient='records') 
            total_inserted = len(data_to_insert)
            
            db.session.bulk_insert_mappings(Books, data_to_insert)
            
            logger.info(f'{total_inserted} novos registros inseridos na tabela books.')

        return jsonify({
            'msg': 'Dados coletados, salvos em CSV e inseridos no banco de dados com sucesso',
            'total_records': total_inserted
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f'error: {e}')
        return jsonify({'error': str(e)}), 500