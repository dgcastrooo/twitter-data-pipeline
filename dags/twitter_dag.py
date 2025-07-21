# DAG de processamento de tweets (placeholder)
# Importações necessárias do Airflow e Python padrão
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import json
import pandas as pd
import os

# Argumentos padrão do DAG (quando inicia e número de tentativas)
default_args = {
    'start_date': datetime(2025, 7, 21),
    'retries': 1,
}

# Função que extrai os dados do arquivo JSON e transforma em Parquet
def extract_and_transform():
    # Caminho do arquivo de entrada JSON
    input_path = os.path.join(os.getcwd(), 'data', 'tweets_sample.json')
    
    # Caminho do arquivo de saída Parquet
    output_path = os.path.join(os.getcwd(), 'data', 'tweets_clean.parquet')

    # Abrindo o arquivo JSON com os tweets
    with open(input_path, 'r', encoding='utf-8') as f:
        tweets = json.load(f)

    # Transformando o JSON em um DataFrame com Pandas
    df = pd.json_normalize(tweets)

    # Selecionando apenas colunas úteis
    df = df[[
        'id',
        'created_at',
        'text',
        'user.id',
        'user.name',
        'user.screen_name',
        'lang'
    ]]

    # Renomeando colunas para nomes mais claros
    df.columns = [
        'tweet_id',
        'created_at',
        'text',
        'user_id',
        'user_name',
        'screen_name',
        'language'
    ]

    # Salvando os dados transformados em formato Parquet
    df.to_parquet(output_path, index=False)
    print("Arquivo Parquet salvo em:", output_path)

# Definição do DAG propriamente dito
with DAG(
    dag_id='twitter_data_pipeline',  # Nome do DAG
    default_args=default_args,       # Argumentos definidos acima
    schedule_interval=None,          # Executado manualmente
    catchup=False,                   # Não executa tarefas antigas
    description='Extrai e transforma tweets para Parquet',
) as dag:

    # Operador Python chamando a função de transformação
    process_tweets = PythonOperator(
        task_id='extract_transform_tweets',      # Nome da tarefa
        python_callable=extract_and_transform    # Função Python a ser chamada
    )

    # Definição da sequência de tarefas (neste caso, só uma)
    process_tweets
