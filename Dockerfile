# Use uma imagem base oficial do Python
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala dependências do sistema necessárias (se houver) e o Poetry
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install poetry

# Configura o Poetry para não criar ambiente virtual (instala no sistema do container)
RUN poetry config virtualenvs.create false

# Copia os arquivos de definição de dependências
COPY pyproject.toml poetry.lock ./

# Instala as dependências do projeto (sem as de desenvolvimento)
RUN poetry install --without dev --no-interaction --no-ansi

# Copia o restante do código da aplicação
COPY . .

# Expõe a porta que a aplicação (Flask) vai rodar
EXPOSE 5000

# Comando para rodar a aplicação
# Nota: É recomendável usar um servidor WSGI como Gunicorn em produção,
# mas para este passo seguiremos com o app.py conforme estrutura atual ou desenvolvimento.
CMD ["python", "app.py"]
