FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install poetry

# Poetry instala libs diretamente no sistema
RUN poetry config virtualenvs.create false

# Copia arquivos de dependência
COPY pyproject.toml poetry.lock ./

# Instala dependências
RUN poetry install --without dev --no-interaction --no-ansi

#Baixar dados do NLTK durante a construção
#RUN python -c "import nltk; nltk.download('punkt_tab'); nltk.download('stopwords')"


# Copia aplicação
COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

EXPOSE 5000

CMD ["python", "app.py"]
