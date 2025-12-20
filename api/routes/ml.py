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


logger = logging.getLogger('__name__')
ml_bp = Blueprint('ml', __name__, url_prefix='/api/v1/ml')

TFIDF_VECTORIZER_PATH = 'data/ml_artifacts/tfidf_vectorizer.pkl'
COSINE_SIM_PATH = 'data/ml_artifacts/cosine_sim_matrix.pkl'
IDX_PATH = 'data/ml_artifacts/idx_series.pkl'


@ml_bp.route('/training-data', methods=['GET'])
@jwt_required()
def training_data():
    '''
    Prepara os dados para treinamento, calcula a matriz de similaridade e salva os artefatos.
    ---
    tags:
        - ML 
    summary: Preparação de dados e artefatos de treinamento.
    description: |
        Lê todos os livros do banco de dados, pré-processa as descrições, calcula a matriz de similaridade do cosseno 
        e salva os artefatos (tfidf, cosine_sim, idx) para uso posterior na predição.
    responses:
        200:
            description: Artefatos de treinamento gerados e salvos com sucesso.
            schema:
                type: object
                properties:
                    msg:
                        type: string
                        description: Mensagem de sucesso.
                    total_records:
                        type: integer
                        description: Número de registros processados.
            examples:
                application/json:
                    msg: 'Dados prontos para treinamento. Artefatos de modelo salvos com sucesso.'
                    total_records: 1000
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
        df = pd.DataFrame([book.to_dict() for book in query])
        
        if df.empty:
            return jsonify({'msg': 'Nenhum dado encontrado no banco de dados para treinamento.'}), 200

        df['description'] = df['description'].fillna('')
        df['description'] = df['description'].apply(tokenizer)
        df = df[df['description'].str.len() > 0].reset_index(drop=True)
        
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(df['description'])
        
        cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
        
        idx = pd.Series(df.index, index=df['title']).drop_duplicates()

        os.makedirs('data/ml_artifacts/', exist_ok=True)

        joblib.dump(tfidf, TFIDF_VECTORIZER_PATH)
        joblib.dump(cosine_sim, COSINE_SIM_PATH)
        joblib.dump(idx, IDX_PATH)
        
        total_records = len(df)
        logger.info(f'Artefatos de modelo salvos: {total_records} registros processados.')

        training_data_json = df[['id', 'title', 'description']].rename(
            columns={'id': 'id'}
        ).to_dict(orient='records')

        return jsonify({
            'msg': 'Dados prontos para treinamento. Artefatos de modelo salvos com sucesso.',
            'total_records': total_records,
            'training_data': training_data_json 
        }), 200

    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/predictions', methods=['GET'])
@jwt_required()
@cache.memoize(timeout=3600)
def predictions():
    '''
    Retorna os 10 livros mais similares a um título fornecido usando os artefatos de treinamento.
    ---
    tags:
        - ml
    summary: Geração de recomendações de livros.
    description: |
        Recebe um título de livro e retorna os 10 mais similares com base na matriz de similaridade do cosseno 
        e nos artefatos salvos na pasta 'data'.
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
            description: Lista dos 10 livros mais similares.
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
    Retorna o histórico de recomendações (preferências) de um usuário específico.
    ---
    tags:
        - ml
    summary: Consulta de histórico de preferências.
    description: |
        Busca na base de dados todos os registros de recomendações gerados anteriormente 
        para um usuário específico, com base no seu ID.
    parameters:
        - name: user_id
          in: path
          type: integer
          required: true
          description: O ID numérico do usuário.
    responses:
        200:
            description: Lista de preferências encontradas.
            schema:
                type: array
                items:
                    type: object
                    properties:
                        id:
                            type: integer
            examples:
                application/json:
                    id: 1
        404:
            description: Histórico não encontrado.
            schema:
                type: object
                properties:
                    msg:
                        type: string
            examples:
                application/json:
                    msg: 'Não há histórico de predições para o usuário id 1.'
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