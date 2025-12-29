import logging
from api.extensions import cache
from flask import Blueprint, jsonify, request
from api.scripts.books_utils import (
    get_all_book_titles, 
    get_book_by_id, 
    get_books_by_title_or_category,
    get_books_by_price_range,
    get_top_rated_books
)
from flask_jwt_extended import jwt_required


logger = logging.getLogger('__name__')
books_bp = Blueprint('books', __name__)


@books_bp.route('/titles', methods=['GET'])
@jwt_required()
@cache.cached(timeout=3600)
def book_titles():
    '''
    Retorna lista com todos os títulos de livros cadastrados 
    ---
    tags:
        - Books
    summary: Listagem de títulos de livros cadastrados.
    description: |
        Endpoint responsável por retornar títulos de livros cadastrados.
    responses:
        200:
            description: Listagem de títulos de livros cadastrados.
            schema:
                type: array
                items:
                    type: string
                    description: Título do livro.
            examples:
                application/json:
                    - title: '10-Day Green Smoothie Cleanse: Lose Up to 15 Pounds in 10 Days!'
                    - title: '13 Hours: The Inside Account of What Really Happened In Benghazi'
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
        titles = get_all_book_titles()
        if titles:
            return jsonify(titles), 200
        return jsonify({'msg': 'Não há livros cadastrados'}), 200
    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': str(e)}), 500


@books_bp.route('/<string:id>', methods=['GET'])
@jwt_required()
@cache.memoize(timeout=3600)
def book_details(id):
    '''
    Retorna detalhes de um livro conforme id fornecido
    ---
    tags:
        - Books
    summary: Detalhes de um livro conforme id fornecido.
    description: |
        Endpoint responsável por retornar detalhes de um livro conforme upc fornecido.
    parameters:
        - in: path
          name: id
          type: integer
          required: true
          description: O id do livro.
    responses:
        200:
            description: Detalhes de um livro conforme código fornecido.
            schema:
                type: object
                properties:
                    id:
                        type: number
                        format: integer
                        description: ID do livro.
                    upc:
                        type: string
                        description: Código do livro.
                    title:
                        type: string
                        description: Título do livro.
                    genre:
                        type: string
                        description: Categoria do livro.
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
                    image_url:
                        type: string
                        description: URL relativa à imagem  do produto.
            examples:
                application/json: 
                    id: 1
                    upc: 'a228380e22709289'
                    title: 'The White Queen'
                    genre: 'Historical'
                    price: 5.99
                    availability: 5
                    rating: 'Five stars'
                    description: 'A description...'
                    product_type: 'books'
                    price_excl_tax: 5.99
                    price_incl_tax: 5.99
                    tax: 0.00
                    number_of_reviews: 1
                    url: 'http://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html'
                    image_url: 'http://books.toscrape.com/media/cache/fe/8a/fe8af6ceec7718986380c0fde9b3b34f.jpg'
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
        404:
            description: Livro não encontrado.
            schema:
                type: object
                properties:
                    msg:
                        type: string
                        description: Mensagem de erro para items não encontrados.
            examples:
                application/json:
                    msg: 'Livro com id 1 não encontrado'
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
        book_details = get_book_by_id(id)
        if book_details:
            return jsonify(book_details), 200
        return jsonify({'msg': f'Livro com id {id} não encontrado'}), 404
    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': str(e)}), 500
    

@books_bp.route('/search', methods=['GET'])
@jwt_required()
@cache.memoize(timeout=3600)
def books_by_title_category():
    '''
    Retorna livros por título e/ou gênero conforme parâmetros fornecidos
    ---
    tags:
        - Books
    summary: Listagem de livros por título e/ou categoria.
    description: |
        Endpoint responsável por retornar lista com informações de livros conforme parâmetros fornecidos. 
    parameters:
        - in: query
          name: title
          type: string
          required: false
          description: Título.
        - in: query
          name: genre
          type: string
          required: false
          description: Gênero.
    responses:
        200:
            description: Listagem de livros por título e/ou gênero.
            schema:
                type: array
                items:
                    type: object
                    properties:
                        id:
                            type: integer
                            description: ID do livro.
                        upc: 
                            type: string
                            description: Código do livro.
                        title: 
                            type: string
                            description: Título do livro.
                        genre: 
                            type: string
                            description: Gênero do livro.
                        price: 
                            type: number
                            format: float
                            description: Preço do livro.
                        image_url:
                            type: string
                            description: URL da imagem do livro.
            examples:
                application/json: 
                    - id: 43
                      upc: 'f684a82adc49f011'
                      title: 'A Murder in Time'
                      genre: 'Mystery'
                      price: 53.98
                      image_url: 'http://books.toscrape.com/media/cache/f6/8e/f68e6ae2f9da04fccbde8442b0a1b52a.jpg'
                    - id: 15
                      upc: 'f733e8c19d40ec2e'
                      title: 'A Murder in Time'
                      genre: 'Mystery'
                      price: 16.64
                      image_url: 'http://books.toscrape.com/media/cache/cc/bd/ccbd7a62caefd5a3a2e04dd7c2ff48fe.jpg'
        400:
            description: Parâmetros ausentes.
            schema:
                type: object
                properties:
                    msg:
                        type: string
                        description: Mensagem de erro para requisição inválida.
            examples:
                application/json:
                    msg: 'Forneça o parâmetro title e/ou genre para a consulta.'
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
        404:
            description: Nenhum livro encontrado com os filtros aplicados.
            schema:
                type: object
                properties:
                    msg:
                        type: string
                        description: Mensagem de erro para items não encontrados.
            examples:
                application/json:
                    msg: 'Nenhum livro encontrado com os parâmetros fornecidos'
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
        title = request.args.get('title')
        genre = request.args.get('genre')
        if not title and not genre:
            return jsonify({'msg': 'Forneça o parâmetro title e/ou genre para a consulta.'}), 400
        books = get_books_by_title_or_category(title=title, genre=genre)
        if books:
            return jsonify(books), 200
        return jsonify({'msg': 'Nenhum livro encontrado com os parâmetros fornecidos'}), 404
    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': str(e)}), 500
    

@books_bp.route('/price-range', methods=['GET'])
@jwt_required()
@cache.memoize(timeout=3600)
def books_by_price_range_route(): 
    '''
    Retorna livros conforme faixa de preço especificada
    ---
    tags:
        - Books
    summary: Listagem de informações de livros conforme faixa de preço especificada.
    description: |
        Endpoint responsável por retornar lista com informações de livros conforme faixa de preço especificada.
    parameters:
        - in: query
          name: min
          type: number
          required: true
          description: Preço mínimo.
        - in: query
          name: max
          type: number
          required: true
          description: Preço máximo.
    responses:
        200:
            description: Listagem de informações de livros conforme faixa de preço especificada.
            schema:
                type: array
                items:
                    type: object
                    properties:
                        id:
                            type: integer
                            description: ID do livro.
                        genre: 
                            type: string
                            description: Categoria do livro.
                        price: 
                            type: number
                            format: float
                            description: Preço do livro.
                        title: 
                            type: string
                            description: Título do livro.
                        upc: 
                            type: string
                            description: Código do livro.
                        image_url:
                            type: string
                            description: URL da imagem do produto.
            examples:
                application/json:
                    - id: 42
                      genre: 'Young Adult'
                      price: 10.0
                      title: 'An Abundance of Katherines'
                      upc: 'f36d24c309e87e5b'
                      image_url: 'http://books.toscrape.com/media/cache/d5/45/d54527d34174d5dd7eaeaaffdfcb3c5c.jpg'
                    - id: 805
                      genre: 'Science'
                      price: 10.01
                      title: 'The Origin of Species'
                      upc: '0345872b14f9e774'
                      image_url: 'http://books.toscrape.com/media/cache/9b/c8/9bc86bc10a6beea536422bbe82e076fb.jpg'
        400:
        400:
            description: Parâmetros ausentes ou inválidos.
            schema:
                type: object
                properties:
                    msg:
                        type: string
                        description: Mensagem de erro para requisição inválida.
            examples:
                application/json:
                    msg: 'Os parâmetros min e max são obrigatórios.'
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
        404:
            description: Nenhum livro encontrado na faixa de preço informada.
            schema:
                type: object
                properties:
                    msg:
                        type: string
                        description: Mensagem de erro para items não encontrados.
            examples:
                application/json:
                    msg: 'Nenhum livro encontrado na faixa de preço.'
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
        min_price = request.args.get('min', type=float)
        max_price = request.args.get('max', type=float)
        if min_price is None or max_price is None:
            return jsonify({'msg': 'Os parâmetros min e max são obrigatórios.'}), 400
        books = get_books_by_price_range(min_price=min_price, max_price=max_price)
        if books:
            return jsonify(books), 200
        return jsonify({'msg': 'Nenhum livro encontrado na faixa de preço informada.'}), 404
    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': str(e)}), 500
    

@books_bp.route('/top-rated', methods=['GET'])
@jwt_required()
@cache.cached(timeout=3600)
def books_top_rated():
    '''
    Retorna lista dos livros com melhor avaliação
    ---
    tags:
        - Books
    summary: Listagem de informações de livros ordenados por avaliação.
    description: |
        Endpoint responsável por retornar lista com informações de livros ordenada por avaliação.
    parameters:
        - in: query
          name: limit
          type: integer
          required: false
          description: Número máximo de livros a retornar.
    responses:
        200:
            description: Listagem de informações de livros ordenados por avaliação.
            schema:
                type: array
                items:
                    type: object
                    properties:
                        id:
                            type: integer
                            description: ID do livro.
                        genre: 
                            type: string
                            description: Gênero do livro.
                        price: 
                            type: number
                            format: float
                            description: Preço do livro.
                        rating:
                            type: string
                            description: Avaliação do livro.
                        title: 
                            type: string
                            description: Título do livro.
                        upc: 
                            type: string
                            description: Código do livro.
                        image_url:
                            type: string
                            description: URL da imagem do livro.
            examples:
                application/json:
                    - id: 11
                      genre: 'Travel'
                      price: 26.08
                      rating: 'Five'
                      title: '1,000 Places to See Before You Die'
                      upc: '228ba5e7577e1d49'
                      image_url: 'http://books.toscrape.com/media/cache/9e/10/9e106f81f65b293e488718a4f54a6a3f.jpg'
                    - id: 993
                      genre: 'Health'
                      price: 49.71
                      rating: 'Five'
                      title: '110-Day Green Smoothie Cleanse: Lose Up to 15 Pounds in 10 Days!'
                      upc: '96aa539bfd4c07e2'
                      image_url: 'http://books.toscrape.com/media/cache/79/84/7984ef7c568a60372f430c1ddae64034.jpg'
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
        404:
            description: Nenhum livro encontrado.
            schema:
                type: object
                properties:
                    msg:
                        type: string
                        description: Mensagem de erro para items não encontrados.
            examples:
                application/json:
                    msg: 'Nenhum livro encontrado'
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
        limit = request.args.get('limit', default=10, type=int)
        books = get_top_rated_books(limit=limit)
        if books:
            return jsonify(books), 200
        return jsonify({'msg': 'Nenhum livro encontrado'}), 404
    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': str(e)}), 500