import logging
from flask import Blueprint, jsonify, request
from api.models.books import (
    get_all_books, get_book_by_upc, 
    get_books_by_title_or_category,
    get_books_by_price_range,
    get_top_rated_books
)
from flask_jwt_extended import jwt_required


logger = logging.getLogger('api.routes.books')
books_bp = Blueprint('books', __name__)


@books_bp.route('/', methods=['GET'])
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
        logger.error(f'error: {e}')
        return jsonify({'error': e}), 401


@books_bp.route('/<string:upc>', methods=['GET'])
@jwt_required()
def book_detail(upc):
    '''
    Retorna todos os detalhes de um livro a partir do seu UPC (Universal Product Code).

    Esta rota consulta o banco de dados usando o UPC fornecido na URL e retorna um objeto JSON
    com todas as informações do livro.
    ---
    tags:
      - Livros
    parameters:
      - in: path
        name: upc
        type: string
        required: true
        description: O UPC (código de produto universal), que é a chave primária do livro.
    responses:
      200:
        description: Detalhes completos do livro.
        schema:
          type: object
          properties:
            upc:
              type: string
              description: Código de Produto Universal (chave primária).
            title:
              type: string
              description: Título principal do livro.
            genre:
              type: string
              description: Gênero ou categoria do livro.
            price:
              type: number
              format: float
              description: Preço do livro.
            availability:
              type: integer
              description: Número de cópias disponíveis em estoque.
            rating:
              type: string
              description: Avaliação do livro (e.g., One star, Two stars).
            description:
              type: string
              description: Descrição completa do livro.
            product_type:
              type: string
              description: Tipo de produto (e.g., books).
            price_excl_tax:
              type: number
              format: float
              description: Preço sem impostos.
            price_incl_tax:
              type: number
              format: float
              description: Preço com impostos incluídos.
            tax:
              type: number
              format: float
              description: Valor do imposto aplicado.
            number_of_reviews:
              type: integer
              description: Contagem total de avaliações.
            url:
              type: string
              description: URL relativa da página do produto.
        examples:
          application/json: 
            upc: "a228380e22709289"
            title: "The White Queen"
            genre: "Historical"
            price: 5.99
            availability: 5
            rating: "Five stars"
            description: "A description..."
            product_type: "books"
            price_excl_tax: 5.99
            price_incl_tax: 5.99
            tax: 0.00
            number_of_reviews: 1
            url: "catalogue/the-white-queen_1/index.html"
      401:
        description: Não autorizado (Requer autenticação JWT).
      404:
        description: Livro não encontrado.
        schema:
          type: object
          properties:
            msg:
              type: string
              description: Mensagem de que o livro não existe.
      500:
        description: Erro interno do servidor.
        schema:
          type: object
          properties:
            error:
              type: string
              description: Mensagem genérica de erro interno.
    '''
    try:
        book_details = get_book_by_upc(upc)
        if book_details:
            return jsonify(book_details), 200
        return jsonify({'msg': f'Livro com UPC {upc} não encontrado'}), 404
    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': e}), 401
    

@books_bp.route('/search', methods=['GET'])
@jwt_required()
def books_title_category():
    '''
    Busca livros por título e-ou categoria usando query parameters.
    ---
    tags:
      - Livros
    parameters:
      - in: query
        name: title
        type: string
        required: false
        description: Título parcial para busca.
      - in: query
        name: genre
        type: string
        required: false
        description: Categoria/gênero parcial para busca.
    responses:
      200:
        description: Lista de livros que correspondem aos critérios de busca.
        schema:
          type: array
          items:
            type: object
            properties:
              upc: {type: string}
              title: {type: string}
              genre: {type: string}
              price: {type: number}
        examples:
          application/json: 
            - upc: "123"
              title: "Livro A"
              genre: "Fantasia"
              price: 10.00
      404:
        description: Nenhum livro encontrado com os filtros aplicados.
      500:
        description: Erro interno do servidor.
    '''
    try:
        title = request.args.get('title')
        genre = request.args.get('genre')
        if not title and not genre:
            return jsonify({'msg': 'Forneça um parâmetro "title" e/ou "genre" para a busca.'}), 400
        books = get_books_by_title_or_category(title=title, genre=genre)
        if books:
            return jsonify(books), 200
        return jsonify({'msg': 'Nenhum livro encontrado com os critérios fornecidos.'}), 404
    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': e}), 500
    

@books_bp.route('/price-range', methods=['GET'])
@jwt_required()
def price_range_books():
    '''
    Filtra livros dentro de uma faixa de preço específica.
    ---
    tags:
      - Livros
    parameters:
      - in: query
        name: min
        type: number
        required: true
        description: Preço mínimo (inclusivo).
      - in: query
        name: max
        type: number
        required: true
        description: Preço máximo (inclusivo).
    responses:
      200:
        description: Lista de livros dentro da faixa de preço.
    '''
    try:
        min_price = request.args.get('min', type=float)
        max_price = request.args.get('max', type=float)
        if min_price is None or max_price is None:
            return jsonify({'msg': 'Os parâmetros "min" e "max" são obrigatórios.'}), 400
        books = get_books_by_price_range(min_price=min_price, max_price=max_price)
        if books:
            return jsonify(books), 200
        return jsonify({'msg': 'Nenhum livro encontrado na faixa de preço.'}), 404
    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': e}), 500
    

@books_bp.route('/top-rated', methods=['GET'])
@jwt_required()
def top_rated_books():
    '''
    Lista os livros com a melhor avaliação (rating mais alto).
    ---
    tags:
      - Livros
    parameters:
      - in: query
        name: limit
        type: integer
        required: false
        description: Número máximo de livros a retornar (Padrão: 10).
    responses:
      200:
        description: Lista dos livros mais bem avaliados.
    '''
    try:
        limit = request.args.get('limit', default=10, type=int)
        books = get_top_rated_books(limit=limit)
        if books:
            return jsonify(books), 200
        return jsonify({'msg': 'Nenhum livro encontrado'}), 404
    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': e}), 500