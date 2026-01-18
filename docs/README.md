# Repositório da API para o Tech Challenge da Fase 1 da Pós-Graduação em Machine Learning Engineering da FIAP

Este repositório consiste em uma API RESTful desenvolvida com Flask, cujo objetivo consistiu no desenvolvimento de uma infraestrutura robusta para a extração, transformação e disponibilização de dados por meio de uma API pública, visando facilitar o consumo dessas informações por cientistas de dados e serviços de recomendação. Para atender aos requisitos, o desenvolvimento pautou-se na implementação de um pipeline ETL automatizado via web scraping, na construção de uma interface escalável e padronizada, na estruturação de uma arquitetura ML-ready para suporte ao ciclo de vida de modelos e na aplicação de protocolos de governança, segurança e rastreabilidade.

Como resultado, a solução consolidou a integração de rotinas de web scraping para aquisição de dados e um motor de recomendação fundamentado em processamento de linguagem natural. No que tange à infraestrutura de serviços, a API passou a dispor de segurança via JSON Web Tokens (JWT) com ciclos de renovação, otimização de performance por meio de camadas de cache e uma robusta camada de observabilidade, que persiste logs de auditoria de todas as transações no banco de dados.

### Arquitetura

O diagrama abaixo ilustra a arquitetura do projeto na sua integridade e com suas principais funcionalidades:

<br><p align='center'><img src='https://github.com/postech-mlengineering/postech-ml-engineering-fase-1-tech-challenge-api/blob/62a2554307c4d75e0631ec8dfb2cf48837e87b58/docs/arquitetura.svg' alt='Arquitetura'></p>

### Pré-requisitos

Certifique-se de ter o Python 3.11, o Poetry 2.1.1 e o Docker 29.1.1 (opcional) instalados em seu sistema.

### Instalação

Clone o repositório e instale as dependências:

```bash
git clone https://github.com/jorgeplatero/postech-ml-techchallenge-fase-1.git

cd postech-ml-techchallenge-fase-1

poetry install
```

O Poetry criará um ambiente virtual isolado e instalará todas as bibliotecas necessárias.

### Como Rodar a Aplicação

**Docker:**

1. Configure as variáveis de ambiente criando um arquivo .env na raiz do projeto e preencha conforme o modelo abaixo:

```bash
JWT_SECRET_KEY=<sua_chave_secreta>
DATABASE_URL=<sua_string_de_conexao>
```

Obs: é possível gerar uma chave segura para o JWT_SECRET_KEY executando:

```bash 
openssl rand -base64 32
```

2. Crie a rede externa (necessária para a comunicação entre os serviços):

```bash
docker network create postech_mlengineering_api
```

3. Inicie a aplicação:

```bash
docker-compose up --build
```

**Local:**

1. Execute as migrações do banco de dados:

```bash
poetry run flask db upgrade
```

Obs: o comando criará o arquivo de banco de dados SQLite automaticamente caso a variável DATABASE_URL não seja fornecida no arquivo .env.

2. Inicie a aplicação:

```bash
poetry run python app.py
```

A API estará rodando em http://127.0.0.1:5000/ e a documentação em http://127.0.0.1:5000/apidocs`.

## Funcionalidades

### Auth (`/api/v1/auth`)

Use estes endpoints para gerenciar o acesso à API.

- **/register**: responsável por registrar usuário e gerar par de tokens JWT
- **/login**: responsável por autenticar o usuário e gerar par de tokens JWT
- **/refresh**: responsável por gerar um novo access token a partir de um refresh token válido

### Books (`/api/v1/books`)

Endpoints para consulta e filtragem do acervo.

- **/titles**: responsável por retornar títulos de livros cadastrados
- **/details/\<book_id\>**: responsável por retornar detalhes de um livro conforme id fornecido
- **/search**: responsável por retornar lista com informações de livros conforme parâmetros fornecidos
- **/price-range**: responsável por retornar lista com informações de livros conforme faixa de preço especificada
- **/top-rated**: responsável por retornar lista com informações de livros ordenada por avaliação

### Genres (`/api/v1/genres`)

- **/**: responsável por retornar lista com gêneros de livros cadastrados

### Web Scraping

- **/scrape**: responsável pelo processo de web scraping e inserção de novos registros na tabela books

### ML (`/api/v1/ml`)

Motor de inteligência artificial para sugestão de conteúdo.

- **/features**: responsável por retornar features para treinamento
- **/training-data**: responsável por realizar o pipeline de treinamento, gerando os artefatos para recomendação de livros
- **/predictions**: responsável por retornar os 10 livros mais similares ao título especificado
- **/user-preferences/\<user_id\>**: responsável por retornar as recomendações para o usuário especificado

### Estatísticas (`/api/v1/stats`)

- **/overview (/overview)**: responsável por retornar estatísticas gerais do acervo
- **/genres (/genres)**: responsável por retornar estatísticas detalhadas por gênero

### Gestão (`/api/v1/health`)

- **/**: Verifica o status da API e a conectividade com o Banco de Dados.

## Monitoramento

A API possui um sistema nativo de monitoramento de performance e auditoria integrada ao ciclo de vida das requisições. Todas as interações são registradas na tabela `access_log`, contendo: 

* **Performance:** tempo de resposta de cada endpoint (response_time_ms), permitindo a identificação de gargalos operacionais e a análise de latência do sistema em tempo real
* **Auditoria:** registro da identidade do usuário autenticado e dos metadados da conexão (endereço IP, sistema operacional e navegador). Inclui a persistência dos parâmetros de busca e do corpo das requisições, garantindo a rastreabilidade dos dados de entrada e a reprodução fiel de estados do sistema para diagnóstico de erros

Esta implementação assegura a governança dos dados e a análise do comportamento de uso da API sem a dependência de serviços externos.

### Tecnologias

| Componente | Tecnologia | Versão | Descrição |
| :--- | :--- | :--- | :--- |
| **Backend/API** | **Flask** | `>=3.1.2, <4.0.0` | Framework para o desenvolvimento de API REST |
| **ORM** | **Flask-SQLAlchemy** | `>=3.1.1, <4.0.0` | Extensão para mapeamento e manipulação de bancos de dados relacionais |
| **Autenticação** | **Flask-JWT-Extended** | `>=4.7.1, <5.0.0` | Extensão para implementação de segurança e controle de acesso via tokens JWT |
| **Criptografia** | **Flask-Bcrypt** | `>=1.0.1, <2.0.0` | Extensão de segurança para hashing e verificação robusta de senhas |
| **Performance** | **Flask-Caching** | `>=2.3.1, <3.0.0` | Extensão de otimização para implementação de camadas de cache |
| **Migrações Flask** | **Flask-Migrate** | `>=4.1.0, <5.0.0` | Extensão que integra o Alembic ao Flask para controle de migrações |
| **Rate Limit** | **Flask-Limiter** | `>=4.1.1, <5.0.0` | Extensão para controle de taxa de requisições |
| **Migrações DB** | **Alembic** | `>=1.17.2, <2.0.0` | Biblioteca de versionamento utilizada para gerenciar migrações e alterações em esquema de banco de dados |
| **Documentação** | **Flasgger** | `>=0.9.7, <0.10.0` | Ferramenta para criação de documentação interativa da API via Swagger (OpenAPI) |
| **Driver DB** | **Psycopg2-binary** | `>=2.9.11, <3.0.0` | Adaptador de banco de dados para conexão com PostgreSQL |
| **Análise de Dados** | **Pandas** | `>=2.3.3, <3.0.0` | Biblioteca para manipulação de dados |
| **Web Scraping** | **BeautifulSoup4** | `>=4.14.2, <5.0.0` | Biblioteca para extração e parseamento de dados de arquivos HTML e XML |
| **Comunicação** | **Requests** | `>=2.32.5, <3.0.0` | Biblioteca para requisições HTTP e consumo de API |
| **NLP** | **NLTK** | `>=3.9.2, <4.0.0` | Biblioteca de processamento de linguagem natural |
| **ML** | **Scikit-learn** | `>=1.7.2, <2.0.0` | Biblioteca para desenvolvimento de modelos de ML |
| **Serialização** | **Joblib** | `>=1.5.2, <2.0.0` | Ferramenta para persistência de modelos de ML e execução de tarefas |
| **Testes** | **Pytest-cov** | `>=7.0.0, <8.0.0` | Extensão para geração de relatórios de cobertura de código nos testes |
| **Configuração** | **Python-dotenv** | `>=1.2.1, <2.0.0` | Biblioteca para carregamento de variáveis de ambiente a partir de arquivos .env |
| **Linguagem** | **Python** | `>=3.11, <3.14` | Linguagem para desenvolvimento de scripts |
| **Infraestrutura** | **Docker** | `29.1.1` | Ferramenta de containerização para paridade entre ambientes |
| **Gerenciamento** | **Poetry** | `2.2.1` | Gerenciador de ambientes virtuais para isolamento de dependências |

### Integrações

Esta API recebe requisições de um aplicativo web desenvolvido com Streamlit e tem suas rotas `\scrape` e `\training-data` orquestradas pelo Apache Airflow.

Link para o repositóro do aplicativo web: https://github.com/postech-mlengineering/postech-ml-techchallenge-fase-1-streamlit

Link para o repositóro do Airflow: https://github.com/postech-mlengineering/postech-ml-engineering-fase-1-techchallenge-airflow

### Deploy

A arquitetura e o deploy foram concebidos para suportar um ecossistema distribuído, utilizando uma instância EC2 na AWS como infraestrutura e Docker para a padronização e o isolamento dos ambientes.

A solução é composta por três camadas de containers integrados:

- **Orquestração (Apache Airflow)**: implementada em containers dedicados, esta camada é responsável pelo agendamento e execução dos pipelines de dados, acionando as rotas de /scrape e /training-data da API

- **API (Flask)**: é o coração da arquitetura. Esta camada interage com o site Books To Scrape para aquisição de dados via web scraping e expõe endpoints para consumo

- **Consumo (Web App Streamlit)**: é a interface web que consome os serviços da API, permitindo que os usuários finais interajam com a API

A comunicação entre os containers é otimizada via Docker network, permitindo a interação entre serviços através de nomes de host em vez de IPs dinâmicos. Essa configuração reduz a latência, elimina custos de tráfego externo e melhora a eficiência ao processar as requisições localmente no host.

Os seviços podem ser acessados nos endereços abaixo:

- **API**: http://18.208.50.37:5000
- **Web App Streamlit**: http://18.208.50.37:8501
- **Apache Airflow**: http://18.208.50.37:8080

#### Persistência

A camada de persistência foi definida em um banco de dados gerenciado via Supabase (integrado à plataforma Vercel). Esta infraestrutura é responsável pela centralização do acervo de livros, pelo histórico de preferências de usuários e pela persistência dos logs de auditoria.

### Link da Apresentação

https://youtu.be/mSAH299OHDs

### Colaboradores

[Jorge Platero](https://github.com/jorgeplatero)

[Leandro Delisposti](https://github.com/LeandroDelisposti)

[Hugo Rodrigues](https://github.com/Nokard)