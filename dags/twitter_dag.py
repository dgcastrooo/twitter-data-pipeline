from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os

from scripts.extract_transform import extract_and_transform
from scripts.upload_to_s3 import upload_to_s3
from scripts.load_to_snowflake import load_to_snowflake

# Argumentos default
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 7, 20),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Definição da DAG
with DAG(
    'twitter_dag',
    default_args=default_args,
    description='Pipeline de dados do Twitter com S3 e Snowflake',
    schedule_interval='@daily',
    catchup=False
) as dag:

    extract_transform_task = PythonOperator(
        task_id='extract_transform_tweets',
        python_callable=extract_and_transform
    )

    upload_task = PythonOperator(
        task_id='upload_to_s3',
        python_callable=upload_to_s3,
        op_kwargs={
            'file_path': '/opt/airflow/data/tweets_clean.parquet',
            'bucket_name': os.getenv("S3_BUCKET_NAME"),
            's3_key': 'tweets/tweets_clean.parquet'
        }
    )

    load_task = PythonOperator(
        task_id='load_to_snowflake',
        python_callable=load_to_snowflake,
        op_kwargs={
            'file_path': '/opt/airflow/data/tweets_clean.parquet'
        }
    )

    extract_transform_task >> upload_task >> load_task
