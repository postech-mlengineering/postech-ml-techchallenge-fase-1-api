import logging
import pandas as pd
import joblib
import os
from flask import Blueprint, jsonify, request
from api.models.books import Books
from api.models.user_preferences import UserPreferences
from api.extensions import db, cache
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from api.scripts.ml_utils import tokenizer, recommender
from flask_jwt_extended import jwt_required, get_jwt_identity


logger = logging.getLogger(__name__)
ml_bp = Blueprint('ml', __name__, url_prefix='/api/v1/ml')

TFIDF_VECTORIZER_PATH = 'data/ml_artifacts/tfidf_vectorizer.pkl'
COSINE_SIM_PATH = 'data/ml_artifacts/cosine_sim_matrix.pkl'
IDX_PATH = 'data/ml_artifacts/idx_series.pkl'


@ml_bp.route('/features', methods=['GET'])
@jwt_required()
def features():
    '''
    Retorna lista com features de treinamento para recomendação de livros
    ---
    tags:
        - ML
    summary: Listagem de features de treinamento para recomendação de livros
    description: |
        Endpoint responsável por retornar features para treinamento.
    responses:
        200:
            description: Listagem de features de treinamento para recomendação de livros
            schema:
                type: object
                properties:
                    features:
                        type: array
                        items:
                            type: object
                            properties:
                                id:
                                    type: integer
                                    description: ID único do livro.
                                title:
                                    type: string
                                    description: Título do livro.
                                description:
                                    type: string
                                    description: Descrição tokenizada (ML-ready).
            examples:
                application/json:
                    features:
                        - id: 1
                          title: "It's Only the Himalayas"
                          description: "wherever whatever dont anything stupid motherduring yearlong adventure..."
                        - id: 2
                          title: "Full Moon over Noah’s Ark: An Odyssey to Mount Ararat and Beyond"
                          description: "acclaimed travel writer rick antonson sets adventurous compass..."
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
        query = db.session.execute(db.select(Books)).scalars().all()
        data = [
            {
                'id': book.id, 
                'title': book.title, 
                'description': tokenizer(book.description) if book.description else ""
            } 
            for book in query
        ]
        return jsonify({
            'total_records': len(data),
            'features': data
        }), 200
    except Exception as e:
        logger.error(f'Erro ao recuperar features: {e}')
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/training-data', methods=['GET'])
@jwt_required()
def training_data():
    '''
    Realiza o pipeline de treinamento para recomendação de livros
    ---
    tags:
        - ML
    summary: Pipeline de treinamento para recomendação de livros
    description: |
        Endpoint responsável por realizar o pipeline de treinamento, gerando os artefatos para recomendação de livros:
        
            - Matriz TF-IDF: uma matriz esparsa de dimensão n×m (onde n é o número de livros e m o vocabulário), onde cada linha representa um vetor de características de um livro e cada célula contém o peso estatístico da importância de um termo no contexto global do dataset
            - Matriz de similaridade: uma matriz quadrada simétrica resultante do cálculo do Produto Escalar (Linear Kernel) entre os vetores da matriz TF-IDF. Ela estabelece a Similaridade de Cosseno, variando de 0 a 1, que quantifica a distância semântica entre todos os pares de livros possíveis
            - Vetor de índices: vetor unidimensional que mapeia títulos para índices, permitindo a indexação e recuperação eficiente das coordenadas correspondentes na matriz de similaridade

        Os arquivos são persistidos em disco (arquivos .joblib) para uso pelo endpoint de predição.
    responses:
        200:
            description: Pipeline de treinamento para recomendação de livros
            schema:
                type: object
                properties:
                    msg:
                        type: string
                        description: Mensagem de sucesso.
                    total_records:
                        type: integer
                        description: Número de registros processados.
                    features:
                        type: array
                        description: Lista de livros processados para o treinamento.
                        items:
                            type: object
                            properties:
                                id:
                                    type: integer
                                    example: 1
                                title:
                                    type: string
                                    example: "It's Only the Himalayas"
                                description:
                                    type: string
                                    example: "wherever whatever dont anything stupid..."
            examples:
                application/json:
                    msg: 'Pipeline de treinamento executado com sucesso'
                    artifacts_saved:
                        - 'tfidf_vectorizer.pkl'
                        - 'cosine_sim_matrix.pkl'
                        - 'idx_series.pkl'
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
        query = db.session.execute(db.select(Books)).scalars().all()
        data = [{'id': book.id, 'title': book.title, 'description': book.description} for book in query]
        df = pd.DataFrame(data)
        
        if df.empty:
            return jsonify({'msg': 'Nenhum dado encontrado para treinamento.'}), 200

        df['description'] = df['description'].fillna('').apply(tokenizer)
        df = df[df['description'].str.len() > 0].reset_index(drop=True)
        
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(df['description'])
        
        cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
        
        idx = pd.Series(df.index, index=df['title']).drop_duplicates()

        os.makedirs('data/ml_artifacts/', exist_ok=True)
        joblib.dump(tfidf, TFIDF_VECTORIZER_PATH)
        joblib.dump(cosine_sim, COSINE_SIM_PATH)
        joblib.dump(idx, IDX_PATH)

        return jsonify({
            'msg': 'Pipeline de treinamento executado com sucesso',
            'artifacts_saved': [
                os.path.basename(TFIDF_VECTORIZER_PATH),
                os.path.basename(COSINE_SIM_PATH),
                os.path.basename(IDX_PATH)
            ]
        }), 200
    except Exception as e:
        logger.error(f'Erro no pipeline de treinamento: {e}')
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/predictions', methods=['GET'])
@jwt_required()
@cache.memoize(timeout=3600)
def predictions():
    '''
    Retorna lista com os 10 livros mais similares ao título especificado
    ---
    tags:
        - ML
    summary: Listagem de livros mais similares.
    description: |
        Endpoint responsável por retornar os 10 livros mais similares ao título especificado.
    parameters:
        - name: body
          in: body
          required: true
          schema:
            type: object
            properties:
              title:
                type: string
                description: O título do livro para o qual se deseja recomendações.
            example:
                title: 'The Secret Garden'
    responses:
        200:
            description: Listagem de livros mais similares.
            schema:
                type: array
                items:
                    type: object
                    properties:
                        title:
                            type: string
                        id:
                            type: integer
                        similarity_score:
                            type: number
        400:
            description: Título não fornecido ou não encontrado.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro para título não fornecido.
            examples:
                application/json:
                    error: 'Título do livro não fornecido.'
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
    data = request.get_json()
    title = data.get('title')

    if not title:
        return jsonify({'error': 'Título do livro não fornecido'}), 400

    try:
        cosine_sim = joblib.load(COSINE_SIM_PATH)
        idx = joblib.load(IDX_PATH)
        
        query = db.session.execute(db.select(Books)).scalars().all()
        df = pd.DataFrame([book.__dict__ for book in query])

        recommendations, error = recommender(title, cosine_sim, df, idx)
        
        if error:
            return jsonify({'error': error}), 400

        user_id = get_jwt_identity()
        if user_id:
            user_id = int(user_id)
        inputed_book_title = df[df['title'] == title]
        inputed_book_id = inputed_book_title['id'].iloc[0] if not inputed_book_title.empty else None
        preferences = []
        try:
            for rec in recommendations:
                preference = UserPreferences(
                    user_id = user_id,
                    inputed_book_title = str(inputed_book_title),
                    inputed_book_id = str(inputed_book_id),
                    recommended_book_id = int(rec['id']),
                    recommended_book_title = str(rec['title']),
                    similarity_score = float(rec['similarity_score'])
                )
                db.session.add(preference)
                preferences.append(preference)
            db.session.commit()

            return jsonify(recommendations), 200

        except Exception as e:
            db.session.rollback()
            logger.error(f'error: {e}')
            return jsonify({'error': str(e)}), 500
    
    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/user-preferences/<int:user_id>', methods=['GET'])
@jwt_required()
@cache.memoize(timeout=3600)
def user_preferences(user_id):
    '''
    Retorna lista com recomendações do usuário especificado
    ---
    tags:
        - ML
    summary: Listagem de recomendações para o usuário especificado.
    description: |
        Endpoint responsável por retornar as recomendações para o usuário especificado.
    parameters:
        - name: user_id
          in: path
          type: integer
          required: true
          description: ID do usuário.
    responses:
        200:
            description: Listagem de recomendações para o usuário especificado.
            schema:
                type: array
                items:
                    type: object
                    properties:
                        id:
                            type: integer
                            description: ID do livro recomendado.
                        title:
                            type: string
                            description: Título do livro.
                        price:
                            type: number
                            format: float
                            description: Preço do livro.
                        rating:
                            type: string
                            description: Avaliação do livro.
                        image_url:
                            type: string
                            description: URL da imagem do livro.
                        similarity_score:
                            type: number
                            format: float
                            description: Score de similaridade calculado.
            examples:
                application/json:
                    - id: 10
                      title: 'Neither Here nor There: Travels in Europe'
                      price: 38.95
                      rating: 'Three'
                      image_url: 'http://books.toscrape.com/media/cache/c9/9a/c99a7a05537cd842eb4db83d537e3a4d.jpg'
                      similarity_score: 0.08789228241825091
                    - id: 11
                      title: '1,000 Places to See Before You Die'
                      price: 26.08
                      rating: 'Five'
                      image_url: 'http://books.toscrape.com/media/cache/9e/10/9e106f81f65b293e488718a4f54a6a3f.jpg'
                      similarity_score: 0.07543122131231231
        404:
            description: Histórico de predições não encontrado.
            schema:
                type: object
                properties:
                    msg:
                        type: string
            examples:
                application/json:
                    msg: 'Não há histórico de predições para o usuário id 1.'
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
    '''
    try:
        query = db.session.query(UserPreferences, Books).join(
            Books, UserPreferences.recommended_book_id == Books.id
        ).filter(
            UserPreferences.user_id == user_id
        ).order_by(
            UserPreferences.similarity_score.desc()
        ).all()
        if not query:
            return jsonify({'msg': f'Não há histórico de predições para o usuário id {user_id}.'}), 404
        results = []
        for pref, book in query:
            results.append({
                'id': book.id,
                'title': book.title,
                'price': book.price,
                'rating': book.rating,
                'image_url': book.image_url,
                'similarity_score': pref.similarity_score,
            })
        return jsonify(results), 200
    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': str(e)}), 500