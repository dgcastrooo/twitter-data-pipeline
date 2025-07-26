from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import pandas as pd
import logging
import re
import html
import tweepy

# Função externa para upload no S3
from scripts.upload_to_s3 import upload_to_s3

# Função externa para carga no Snowflake
from scripts.load_to_snowflake import main as load_to_snowflake_main

default_args = {
    'owner': 'diogo',
    'start_date': datetime(2025, 7, 21),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
}

# Função de extração e transformação dos tweets
def extract_and_transform():
    logging.basicConfig(level=logging.INFO)
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

    if not bearer_token:
        raise ValueError("Variável de ambiente TWITTER_BEARER_TOKEN não está definida.")

    client = tweepy.Client(bearer_token=bearer_token)

    query = "data engineering -is:retweet lang:pt"

    response = client.search_recent_tweets(
        query=query,
        tweet_fields=["id", "text", "created_at", "lang"],
        expansions=["author_id"],
        user_fields=["id", "name", "username"],
        max_results=100
    )

    if not response.data:
        raise ValueError("Nenhum tweet retornado pela API.")

    tweets = response.data
    users = {user.id: user for user in response.includes["users"]}

    data = []
    for tweet in tweets:
        user = users.get(tweet.author_id)
        data.append({
            "tweet_id": tweet.id,
            "created_at": tweet.created_at,
            "text": tweet.text,
            "user_id": user.id if user else None,
            "user_name": user.name if user else None,
            "screen_name": user.username if user else None,
            "language": tweet.lang
        })

    df = pd.DataFrame(data)

    if df.empty:
        raise ValueError("DataFrame resultante está vazio.")

    # Limpa texto de HTML e espaços
    def clean_html(text):
        try:
            if not isinstance(text, str):
                return text
            text = html.unescape(text)
            text = re.sub(r"<[^>]+>", "", text)
            text = re.sub(r"[\r\n\t]+", " ", text)
            text = re.sub(r"\s+", " ", text)
            return text.strip()
        except Exception as e:
            logging.warning(f"Erro ao limpar texto: {e}")
            return text

    df["text"] = df["text"].apply(clean_html)

    # Salva em formato parquet
    output_path = os.path.join(os.getcwd(), 'data', 'tweets_clean.parquet')
    df.to_parquet(output_path, index=False)
    logging.info(f"Arquivo Parquet salvo com sucesso em: {output_path}")

# Função que faz upload para o S3
def upload():
    file_path = '/opt/airflow/data/tweets_clean.parquet'
    bucket_name = 'twitter-data-pipeline-diogo'
    s3_key = 'twitter/tweets_clean.parquet'
    upload_to_s3(file_path, bucket_name, s3_key)

# Função que carrega dados para o Snowflake
def load_to_snowflake():
    load_to_snowflake_main()

# Definição da DAG
with DAG(
    dag_id='twitter_dag',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    description='Extrai, limpa, envia tweets para S3 e carrega no Snowflake',
) as dag:

    extract_transform_task = PythonOperator(
        task_id='extract_transform_tweets',
        python_callable=extract_and_transform
    )

    upload_task = PythonOperator(
        task_id='upload_to_s3',
        python_callable=upload
    )

    load_snowflake_task = PythonOperator(
        task_id='load_to_snowflake',
        python_callable=load_to_snowflake
    )

    # Define a ordem das tasks: Extração → Upload → Snowflake
    extract_transform_task >> upload_task >> load_snowflake_task
