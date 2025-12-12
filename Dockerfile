FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instala o Poetry (método recomendado)
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Poetry instala libs diretamente no sistema
RUN poetry config virtualenvs.create false

# Copia arquivos de dependência
COPY pyproject.toml poetry.lock ./

# Instala dependências
RUN poetry install --without dev --no-interaction --no-ansi

# Copia aplicação
COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

EXPOSE 5000

CMD ["python", "app.py"]
