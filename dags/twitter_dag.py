from airflow import DAG  # Importa a classe DAG para definir o fluxo de trabalho
from airflow.operators.python import PythonOperator  # Importa operador para tarefas Python
from datetime import datetime, timedelta  # Importa para controle de datas e intervalos
import os  # Módulo para manipulação de caminhos de arquivos
import json  # Módulo para manipulação de arquivos JSON
import pandas as pd  # Biblioteca para manipulação de dados
import logging  # Biblioteca para logs estruturados
from scripts.upload_to_s3 import upload_to_s3  # Script auxiliar para carregar os arquivos no S3

default_args = {
    'owner': 'diogo',  # Responsável pelo DAG
    'start_date': datetime(2025, 7, 21),  # Data inicial para o DAG começar a rodar
    'retries': 1,  # Número de tentativas em caso de falha
    'retry_delay': timedelta(minutes=5),  # Tempo de espera entre tentativas
    'email_on_failure': False,  # Não enviar e-mail em caso de falha
}

def extract_and_transform():  # Função para extração e transformação dos dados
    logging.basicConfig(level=logging.INFO)  # Configura o nível de logs para INFO

    input_path = os.path.join(os.getcwd(), 'data', 'tweets_sample.json')  # Caminho do arquivo JSON de entrada
    output_path = os.path.join(os.getcwd(), 'data', 'tweets_clean.parquet')  # Caminho do arquivo Parquet de saída

    logging.info(f"Iniciando extração de dados do arquivo: {input_path}")  # Log da etapa de início

    if not os.path.exists(input_path):  # Verifica se o arquivo JSON existe
        raise FileNotFoundError(f"❌ Arquivo JSON não encontrado em: {input_path}")  # Erro caso não exista

    with open(input_path, 'r', encoding='utf-8') as f:  # Abre o arquivo JSON para leitura
        tweets = json.load(f)  # Carrega o conteúdo JSON

    df = pd.json_normalize(tweets)  # Normaliza o JSON aninhado para DataFrame plano
    logging.info("✅ JSON carregado e normalizado com sucesso.")  # Log da normalização feita

    if df.empty:  # Valida se o DataFrame está vazio
        raise ValueError("❌ DataFrame resultante está vazio.")  # Erro caso não haja dados

    required_columns = ['id', 'created_at', 'text']  # Colunas essenciais para validação
    for col in required_columns:  # Loop para checar cada coluna obrigatória
        if col not in df.columns:  # Se faltar alguma coluna
            raise ValueError(f"❌ Coluna obrigatória ausente: {col}")  # Erro específico

    df = df[['id', 'created_at', 'text', 'user.id', 'user.name', 'user.screen_name', 'lang']]  # Seleção de colunas úteis
    df.columns = ['tweet_id', 'created_at', 'text', 'user_id', 'user_name', 'screen_name', 'language']  # Renomeia colunas para clareza

    df.to_parquet(output_path, index=False)  # Salva o DataFrame como arquivo Parquet sem índice
    logging.info(f"✅ Arquivo Parquet salvo com sucesso em: {output_path}")  # Log de sucesso na gravação

def upload():  # Função que faz o upload do arquivo transformado para o S3
    file_path = '/opt/airflow/data/tweets_clean.parquet'  # Caminho do arquivo local (dentro do container)
    bucket_name = 'twitter-data-pipeline-diogo '  # Substitua pelo nome do seu bucket
    s3_key = 'twitter/tweets_clean.parquet'  # Caminho destino no bucket
    upload_to_s3(file_path, bucket_name, s3_key)  # Chama a função de upload

with DAG(
    dag_id='twitter_data_pipeline',  # Identificador único do DAG
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
