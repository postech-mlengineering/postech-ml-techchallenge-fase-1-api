import logging
from flask import Blueprint, jsonify
from flask_bcrypt import Bcrypt
from api.models.books import get_all_books
from flask_jwt_extended import jwt_required


bcrypt = Bcrypt()
logger = logging.getLogger('api.auth')

books_bp = Blueprint('books', __name__)
@books_bp.route('/books', methods=['GET'])
@jwt_required()
def books():
    '''
    Retorna a lista de todos os titulos de livros cadastrados no sistema.
    ---
    tags:
      - Livros
    responses:
      200:
        description: Lista do titulo dos livros ou mensagem de que não há livros.
        schema:
          type: array
          items:
            type: object
            properties:
              titulo:
                type: string
                description: Título principal do livro.
        examples:
          application/json: 
            - id: 101
              titulo: O Senhor dos Anéis
            - id: 102
              titulo: 1984
      401:
        description: Erro interno do servidor.
        schema:
          type: object
          properties:
            error:
              type: string
              description: Mensagem de erro capturada pela exceção.
    '''
    try:
        books = get_all_books()
        if books:
            return jsonify(books), 200
        return jsonify({'msg': 'Sem livros cadastrados'}), 200
    except Exception as e:
        return jsonify({'error': e}), 401
