from airflow import DAG  # Importa a classe DAG para definir o fluxo de trabalho
from airflow.operators.python import PythonOperator  # Importa operador para tarefas Python
from datetime import datetime, timedelta  # Importa para controle de datas e intervalos
import os  # Módulo para manipulação de caminhos de arquivos
import json  # Módulo para manipulação de arquivos JSON
import pandas as pd  # Biblioteca para manipulação de dados
import logging  # Biblioteca para logs estruturados
from scripts.upload_to_s3 import upload_to_s3  # Script auxiliar para carregar os arquivos no S3
import tweepy

default_args = {
    'owner': 'diogo',  # Responsável pelo DAG
    'start_date': datetime(2025, 7, 21),  # Data inicial para o DAG começar a rodar
    'retries': 1,  # Número de tentativas em caso de falha
    'retry_delay': timedelta(minutes=5),  # Tempo de espera entre tentativas
    'email_on_failure': False,  # Não enviar e-mail em caso de falha
}

def extract_and_transform():  # Função para extrair tweets da API e salvar como Parquet
    logging.basicConfig(level=logging.INFO)  # Configura o nível de logs para INFO

    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")  # Recupera o token de autenticação do ambiente

    if not bearer_token:  # Verifica se o token está presente
        raise ValueError("Variável de ambiente TWITTER_BEARER_TOKEN não está definida.")  # Erro se faltar o token

    client = tweepy.Client(bearer_token=bearer_token)  # Inicializa o cliente da API com o token

    query = "data engineering -is:retweet lang:pt"  # Termo de busca: tweets sobre data engineering, em português, excluindo retweets

    response = client.search_recent_tweets(  # Realiza a busca por tweets recentes
        query=query,  # Termo de busca
        tweet_fields=["id", "text", "created_at", "lang"],  # Campos a serem retornados do tweet
        expansions=["author_id"],  # Expande os dados do autor
        user_fields=["id", "name", "username"],  # Campos do usuário autor
        max_results=100  # Quantidade máxima de tweets retornados (limite da API)
    )

    if not response.data:  # Verifica se algum tweet foi retornado
        raise ValueError("Nenhum tweet retornado pela API.")  # Erro se a resposta estiver vazia

    tweets = response.data  # Lista de objetos Tweet
    users = {user.id: user for user in response.includes["users"]}  # Mapeia usuários por ID

    data = []  # Lista para armazenar os dados extraídos

    for tweet in tweets:  # Itera sobre cada tweet retornado
        user = users.get(tweet.author_id)  # Busca o autor do tweet
        data.append({  # Adiciona os dados do tweet e do usuário
            "tweet_id": tweet.id,
            "created_at": tweet.created_at,
            "text": tweet.text,
            "user_id": user.id if user else None,
            "user_name": user.name if user else None,
            "screen_name": user.username if user else None,
            "language": tweet.lang
        })

    df = pd.DataFrame(data)  # Converte a lista de dicionários para DataFrame

    if df.empty:  # Verifica se o DataFrame está vazio
        raise ValueError("DataFrame resultante está vazio.")  # Erro caso não haja dados válidos

    output_path = os.path.join(os.getcwd(), 'data', 'tweets_clean.parquet')  # Caminho de saída do arquivo Parquet

    df.to_parquet(output_path, index=False)  # Salva o DataFrame em formato Parquet
    logging.info(f"Arquivo Parquet salvo com sucesso em: {output_path}")  # Log de sucesso



def upload():  # Função que faz o upload do arquivo transformado para o S3
    file_path = '/opt/airflow/data/tweets_clean.parquet'  # Caminho do arquivo local (dentro do container)
    bucket_name = 'twitter-data-pipeline-diogo'  # Nome do bucket
    s3_key = 'twitter/tweets_clean.parquet'  # Caminho destino no bucket
    upload_to_s3(file_path, bucket_name, s3_key)  # Chama a função de upload



with DAG(
    dag_id='twitter_dag',  # Identificador único do DAG
    default_args=default_args,  # Argumentos padrão do DAG
    schedule_interval=None,  # Não agendado automaticamente, roda manualmente
    catchup=False,  # Não executa runs antigos que não foram executados
    description='Extrai e transforma tweets com validação e logs',  # Descrição do DAG
) as dag:

    extract_transform_task = PythonOperator(  # Task de extração e transformação
        task_id='extract_transform_tweets',  # Nome da task
        python_callable=extract_and_transform  # Função Python chamada
    )

    upload_task = PythonOperator(  # Task que realiza o upload para o S3
        task_id='upload_to_s3',  # Nome da task
        python_callable=upload  # Função Python chamada
    )

    extract_transform_task >> upload_task  # Executa upload após extração e transformação
