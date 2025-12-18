# 📚 API de Gerenciamento de Livros com Sistema de Recomendação ML

API REST desenvolvida em Flask para o Tech Challenge da Fase 1 da Pós-Graduação em Machine Learning Engineering da FIAP. A aplicação oferece funcionalidades de gerenciamento de livros, autenticação JWT, web scraping e um sistema de recomendação baseado em conteúdo usando Machine Learning.

## 🎯 Funcionalidades

- **Autenticação JWT**: Sistema completo de registro, login e refresh tokens
- **Gerenciamento de Livros**: CRUD completo com busca e filtros avançados
- **Web Scraping**: Coleta automática de dados de livros
- **Sistema de Recomendação ML**: Recomenda livros similares baseado em conteúdo (TF-IDF + Cosine Similarity)
- **Estatísticas**: Análise de dados dos livros cadastrados
- **Categorias**: Gerenciamento de categorias de livros

## 🏗️ Arquitetura

```mermaid
graph TB
    Client[Cliente/Frontend] -->|HTTP Requests| API[Flask API]
    API --> Auth[Auth Routes]
    API --> Books[Books Routes]
    API --> ML[ML Routes]
    API --> Scrape[Scrape Routes]
    API --> Stats[Stats Routes]
    
    Auth --> DB[(PostgreSQL)]
    Books --> DB
    ML --> DB
    ML --> Artifacts[ML Artifacts<br/>TF-IDF, Cosine Sim]
    Scrape --> DB
    Stats --> DB
    
    Scrape --> Web[Web Scraping<br/>Books.toscrape.com]
    
    style API fill:#4A90E2
    style DB fill:#336791
    style Artifacts fill:#FF6B6B
```

## 📊 Fluxos Principais

### 1. Fluxo de Autenticação

```mermaid
sequenceDiagram
    participant C as Cliente
    participant API as API Flask
    participant DB as PostgreSQL
    participant JWT as JWT Manager
    
    Note over C,JWT: Registro de Usuário
    C->>API: POST /api/v1/auth/register<br/>{username, password}
    API->>DB: Verifica se usuário existe
    alt Usuário não existe
        API->>API: Hash da senha (bcrypt)
        API->>DB: Insere novo usuário
        API->>C: 201 - Usuário criado
    else Usuário já existe
        API->>C: 400 - Usuário já existe
    end
    
    Note over C,JWT: Login
    C->>API: POST /api/v1/auth/login<br/>{username, password}
    API->>DB: Busca usuário
    API->>API: Valida senha (bcrypt)
    alt Credenciais válidas
        API->>DB: Registra acesso (UserAccess)
        API->>DB: Verifica refresh token existente
        alt Refresh token válido existe
            API->>JWT: Gera novo access token
            API->>C: 200 - {access_token, refresh_token}
        else Não existe refresh token
            API->>JWT: Gera access + refresh tokens
            API->>DB: Salva refresh token
            API->>C: 200 - {access_token, refresh_token}
        end
    else Credenciais inválidas
        API->>C: 401 - Credenciais inválidas
    end
    
    Note over C,JWT: Refresh Token
    C->>API: POST /api/v1/auth/refresh<br/>Header: Bearer {refresh_token}
    API->>JWT: Valida refresh token
    API->>DB: Verifica refresh token no banco
    alt Token válido
        API->>JWT: Gera novo access token
        API->>C: 200 - {access_token}
    else Token inválido/expirado
        API->>C: 401 - Token inválido/expirado
    end
```

### 2. Fluxo de Recomendação ML

```mermaid
flowchart TD
    Start([Início: Requisição de Recomendação]) --> LoadArtifacts[Carregar Artefatos ML<br/>- Cosine Similarity Matrix<br/>- Index Series]
    
    LoadArtifacts --> CheckArtifacts{Artefatos<br/>existem?}
    CheckArtifacts -->|Não| Error1[Erro 500:<br/>Artefatos não encontrados]
    CheckArtifacts -->|Sim| LoadBooks[Carregar todos os livros<br/>do banco de dados]
    
    LoadBooks --> ConvertDF[Converter para DataFrame<br/>pandas]
    ConvertDF --> GetTitleIndex[Buscar índice do título<br/>no idx_series]
    
    GetTitleIndex --> CheckTitle{Título<br/>encontrado?}
    CheckTitle -->|Não| Error2[Erro 400:<br/>Título não encontrado]
    CheckTitle -->|Sim| GetSimilarity[Obter scores de similaridade<br/>da matriz cosine_sim]
    
    GetSimilarity --> SortScores[Ordenar por similaridade<br/>decrescente]
    SortScores --> GetTop10[Selecionar top 10<br/>excluindo o próprio livro]
    
    GetTop10 --> FormatResponse[Formatar resposta com:<br/>- title<br/>- id<br/>- similarity_score]
    FormatResponse --> Return[Retornar JSON<br/>com recomendações]
    
    Error1 --> End([Fim])
    Error2 --> End
    Return --> End
    
    style Start fill:#4A90E2
    style Return fill:#51CF66
    style Error1 fill:#FF6B6B
    style Error2 fill:#FF6B6B
    style End fill:#868E96
```

### 3. Fluxo de Treinamento do Modelo ML

```mermaid
flowchart LR
    Start([GET /api/v1/ml/training-data]) --> LoadBooks[Carregar livros<br/>do banco]
    LoadBooks --> CheckEmpty{DataFrame<br/>vazio?}
    CheckEmpty -->|Sim| ReturnEmpty[Retornar:<br/>Nenhum dado encontrado]
    CheckEmpty -->|Não| FillNA[Preencher descrições<br/>vazias com '']
    
    FillNA --> Tokenize[Aplicar tokenizer:<br/>- Normalizar acentos<br/>- Remover pontuação<br/>- Remover stopwords<br/>- Remover números]
    Tokenize --> FilterEmpty[Filtrar descrições<br/>vazias]
    
    FilterEmpty --> TFIDF[Aplicar TF-IDF<br/>Vectorizer]
    TFIDF --> CosineSim[Calcular Matriz de<br/>Similaridade do Cosseno]
    CosineSim --> CreateIndex[Criar índice<br/>title -> position]
    
    CreateIndex --> SaveArtifacts[Salvar Artefatos:<br/>- tfidf_vectorizer.pkl<br/>- cosine_sim_matrix.pkl<br/>- idx_series.pkl]
    SaveArtifacts --> ReturnSuccess[Retornar:<br/>- Mensagem de sucesso<br/>- Total de registros<br/>- Dados de treinamento]
    
    ReturnEmpty --> End([Fim])
    ReturnSuccess --> End
    
    style Start fill:#4A90E2
    style SaveArtifacts fill:#FFD93D
    style ReturnSuccess fill:#51CF66
    style End fill:#868E96
```

### 4. Fluxo de Web Scraping

```mermaid
sequenceDiagram
    participant C as Cliente
    participant API as API Flask
    participant Scraper as Scrape Utils
    participant Web as Books.toscrape.com
    participant CSV as Arquivo CSV
    participant DB as PostgreSQL
    
    C->>API: POST /api/v1/scrape/scrape-and-insert
    API->>Scraper: run_scraping_and_save_data()
    
    loop Para cada página
        Scraper->>Web: Requisição HTTP
        Web->>Scraper: HTML da página
        Scraper->>Scraper: Parse HTML (BeautifulSoup)
        Scraper->>Scraper: Extrair dados dos livros
    end
    
    Scraper->>CSV: Salvar dados em CSV
    Scraper->>API: Retornar DataFrame
    
    API->>DB: TRUNCATE TABLE books
    API->>DB: Bulk Insert dos dados
    DB->>API: Confirmação
    
    API->>C: 200 - Dados coletados e inseridos<br/>{msg, total_records}
```

### 5. Fluxo de Busca de Livros

```mermaid
flowchart TD
    Start([GET /api/v1/books/search]) --> ValidateToken{Token JWT<br/>válido?}
    ValidateToken -->|Não| Error401[401 - Erro de autenticação]
    ValidateToken -->|Sim| GetParams[Obter parâmetros:<br/>title, genre]
    
    GetParams --> CheckParams{Parâmetros<br/>fornecidos?}
    CheckParams -->|Não| Error400[400 - Parâmetros ausentes]
    CheckParams -->|Sim| QueryDB[Consultar banco de dados<br/>com filtros]
    
    QueryDB --> CheckResults{Resultados<br/>encontrados?}
    CheckResults -->|Não| Error404[404 - Nenhum livro encontrado]
    CheckResults -->|Sim| FormatResponse[Formatar resposta JSON]
    
    FormatResponse --> Return200[200 - Lista de livros]
    
    Error401 --> End([Fim])
    Error400 --> End
    Error404 --> End
    Return200 --> End
    
    style Start fill:#4A90E2
    style Return200 fill:#51CF66
    style Error401 fill:#FF6B6B
    style Error400 fill:#FF6B6B
    style Error404 fill:#FF6B6B
    style End fill:#868E96
```

## 🚀 Instalação

### Pré-requisitos

- Python 3.11+
- PostgreSQL
- Poetry (gerenciador de dependências)

### Passos

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd postech-ml-techchallenge-fase-1-api
```

2. **Instale as dependências**
```bash
poetry install
```

3. **Configure as variáveis de ambiente**
```bash
# Copie o arquivo de exemplo e configure
cp .env.example .env
```

Configure as seguintes variáveis no arquivo `.env`:
- `DATABASE_URL`: URL de conexão com PostgreSQL
- `JWT_SECRET_KEY`: Chave secreta para JWT
- `JWT_ACCESS_TOKEN_EXPIRES`: Tempo de expiração do access token
- `JWT_REFRESH_TOKEN_EXPIRES`: Tempo de expiração do refresh token

4. **Execute as migrações**
```bash
poetry run alembic upgrade head
```

5. **Inicie o servidor**
```bash
poetry run python app.py
```

A API estará disponível em `http://localhost:5000`

## 📁 Estrutura do Projeto

```
postech-ml-techchallenge-fase-1-api/
├── api/
│   ├── __init__.py              # Factory do Flask app
│   ├── config/
│   │   └── config.py            # Configurações da aplicação
│   ├── models/
│   │   ├── __init__.py          # Inicialização do SQLAlchemy
│   │   ├── books.py             # Modelo Books
│   │   ├── user.py              # Modelo User
│   │   ├── users_access.py      # Modelo UserAccess
│   │   └── refresh_token_manager.py  # Modelo RefreshTokenManager
│   ├── routes/
│   │   ├── auth.py              # Rotas de autenticação
│   │   ├── books.py             # Rotas de livros
│   │   ├── categories.py        # Rotas de categorias
│   │   ├── health.py            # Health check
│   │   ├── ml.py                # Rotas de ML
│   │   ├── scrape.py            # Rotas de scraping
│   │   └── stats.py             # Rotas de estatísticas
│   ├── scripts/
│   │   ├── books_utils.py       # Utilitários de livros
│   │   ├── ml_utils.py          # Utilitários de ML
│   │   ├── scrape_utils.py      # Utilitários de scraping
│   │   └── user_utils.py        # Utilitários de usuário
│   └── logs/
│       └── routes_middleware.py # Middleware de logging
├── migrations/                  # Migrações Alembic
├── tests/                       # Testes
├── data/
│   ├── books.csv                # Dados de livros
│   └── ml_artifacts/            # Artefatos de ML
├── app.py                       # Entry point
├── pyproject.toml               # Dependências Poetry
└── README.md                    # Este arquivo
```

## 🔧 Tecnologias Utilizadas

- **Flask**: Framework web
- **SQLAlchemy**: ORM para banco de dados
- **PostgreSQL**: Banco de dados relacional
- **Flask-JWT-Extended**: Autenticação JWT
- **Flask-Bcrypt**: Hash de senhas
- **Pandas**: Manipulação de dados
- **Scikit-learn**: Machine Learning (TF-IDF, Cosine Similarity)
- **BeautifulSoup4**: Web scraping
- **NLTK**: Processamento de linguagem natural
- **Flasgger**: Documentação Swagger
- **Alembic**: Migrações de banco de dados
- **Poetry**: Gerenciamento de dependências

## 📝 Endpoints Principais

### Autenticação
- `POST /api/v1/auth/register` - Registrar novo usuário
- `POST /api/v1/auth/login` - Login e obtenção de tokens
- `POST /api/v1/auth/refresh` - Renovar access token

### Livros
- `GET /api/v1/books/titles` - Listar todos os títulos
- `GET /api/v1/books/<id>` - Detalhes de um livro
- `GET /api/v1/books/search?title=&genre=` - Buscar livros
- `GET /api/v1/books/price-range?min=&max=` - Filtrar por preço
- `GET /api/v1/books/top-rated?limit=` - Top livros por avaliação

### Machine Learning
- `GET /api/v1/ml/training-data` - Treinar modelo e gerar artefatos
- `GET /api/v1/ml/predictions` - Obter recomendações de livros

### Web Scraping
- `POST /api/v1/scrape/scrape-and-insert` - Executar scraping e inserir dados

### Documentação
- `GET /apidocs` - Documentação Swagger interativa

## 🔐 Segurança

- Autenticação JWT com access e refresh tokens
- Hash de senhas com bcrypt
- Validação de tokens em rotas protegidas
- Middleware de logging de requisições

## 🧪 Testes

Execute os testes com:
```bash
poetry run pytest
```

## 📄 Licença

MIT License

## 👥 Autores

- jorge Platero [Linkedin](https://www.linkedin.com/in/jorgeplatero/)
- Hugo Rodrigues [Linkedin](https://www.linkedin.com/in/hugo-rodrigues-dias/)
- Leandro [Linkedin](https://www.linkedin.com/in/leandro-delisposti/)
---

**Desenvolvido para o Tech Challenge da Fase 1 da Pós-Graduação em Machine Learning Engineering da FIAP**

