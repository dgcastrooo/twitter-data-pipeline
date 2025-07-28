
# 🐦 Twitter Data Pipeline

Este projeto implementa um pipeline de dados moderno utilizando **Apache Airflow**, **AWS S3** e **Snowflake** para orquestrar a ingestão, transformação e carregamento de tweets. Ideal para fins de portfólio, aprendizado ou projetos de engenharia de dados em produção.

## 📌 Visão Geral

O pipeline realiza as seguintes etapas:

1. **Extração**: carrega tweets de um arquivo `.json`.
2. **Transformação**: normaliza e limpa os dados, convertendo para `.parquet`.
3. **Armazenamento**: envia o `.parquet` para um bucket AWS S3.
4. **Carga final**: carrega os dados do `.parquet` do S3 para uma tabela Snowflake.

## 🛠️ Tecnologias Utilizadas

- **Python 3.11**
- **Apache Airflow**
- **Docker + Docker Compose**
- **AWS S3**
- **Snowflake**
- **Pandas**
- **Boto3 (AWS SDK)**
- **Snowflake Connector for Python**

## 🗂️ Estrutura do Projeto

```
twitter-data-papeline-main/
├── dags/                      # DAG principal do Airflow
│   └── twitter_dag.py
├── scripts/                   # Scripts de integração com S3 e Snowflake
│   ├── extract_and_transform.py
│   └── load_to_snowflake.py
│   └── upload_to_s3.py 
├── data/                      # Dados de exemplo
│   └── tweets_sample.json
├── config/
│   └── config_example.yaml    # Configurações sensíveis (ex: S3, Snowflake)
├── docker-compose.yaml        # Ambientes Airflow
├── requirements.txt           # Dependências Python
├── .env                       # Variáveis de ambiente (Airflow, AWS, Snowflake)
```

## 🔁 Fluxo do Pipeline

A DAG do Airflow executa as seguintes tarefas:

1. **Extrair dados do JSON**
2. **Transformar para .parquet**
3. **Fazer upload para AWS S3**
4. **Carregar no Snowflake**

## 📸 Diagrama do Pipeline

<p align="center">
  <img src="pipeline_diagram.png" width="600px">
</p>

## ▶️ Como Executar Localmente

### Pré-requisitos

- Docker + Docker Compose
- Conta na AWS com bucket S3 criado
- Conta na Snowflake com:
  - Warehouse: `COMPUTE_WH`
  - Database: `TWITTER_DATA_PIPELINE`
  - Schema: `RAW_DATA`
  - Tabela: `tweets` criada previamente

### 1. Clone o projeto

```bash
git clone https://github.com/dgcastrooo/twitter-data-papeline.git
cd twitter-data-papeline
```

### 2. Configure suas variáveis

Crie o arquivo `.env` com as seguintes variáveis (exemplo):

```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_BUCKET_NAME=your_bucket_name
AWS_REGION=sa-east-1

SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=TWITTER_DATA_PIPELINE
SNOWFLAKE_SCHEMA=RAW_DATA
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_TABLE=tweets
```

### 3. Suba os containers

```bash
docker-compose up -d
```

### 4. Acesse o Airflow

Abra no navegador:

```
http://localhost:8080
```

Login padrão:

- **Usuário:** `airflow`
- **Senha:** `airflow`

## ✅ Status das Tarefas

- [x] Extração de dados do JSON
- [x] Transformação para Parquet
- [x] Upload para AWS S3
- [x] Carga para Snowflake
- [x] Orquestração via Airflow

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

## 🙋‍♂️ Autor

**Diogo José Castro de Carvalho Pereira**  
[LinkedIn](https://www.linkedin.com/in/dgcastrooo/) • [GitHub](https://github.com/dgcastrooo)
