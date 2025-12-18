import logging
import nltk
import re
import string
import unicodedata
from nltk.tokenize import word_tokenize
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')
from nltk.corpus import stopwords

logger = logging.getLogger('api.scripts.ml_utils')

def normalize_accents(text):
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')


def remove_punctuation(text):
    punctuations = string.punctuation
    table = str.maketrans({key: ' ' for key in punctuations})
    text = text.translate(table)
    return text


def normalize_str(text):
    text = text.lower()
    text = remove_punctuation(text)
    text = normalize_accents(text)
    text = re.sub(re.compile(r' +'), ' ', text)
    return ' '.join([w for w in text.split()])


def tokenizer(text):
    stop_words = nltk.corpus.stopwords.words('english')
    if isinstance(text, str):
        text = normalize_str(text)
        text = ''.join([w for w in text if not w.isdigit()])
        text = word_tokenize(text)
        text = [x for x in text if x not in stop_words]
        text = [y for y in text if len(y) > 2]
        return ' '.join([t for t in text])
    else:
        return None
    

def content_recommender(title, cosine_sim, df, idx):
    '''
    Função de recomendação baseada no conteúdo.
    '''
    if title not in idx:
        return None, f'O título "{title}" não foi encontrado na base de dados.'
    idx = idx[title]

    sim_scores = list(enumerate(cosine_sim[idx]))

    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    #obtendo os scores dos 10 mais similares, ignorando o primeiro (o próprio livro)
    sim_scores = sim_scores[1:11]

    idx = [i[0] for i in sim_scores]
    
    recommendations = df.iloc[idx][['title', 'id']].to_dict(orient='records')
    
    for i, rec in enumerate(recommendations):
        rec['similarity_score'] = sim_scores[i][1]
    
    return recommendations, None