import os
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv

def load_to_snowflake(file_path: str):
    # Carrega variáveis do .env local
    load_dotenv()

    # Conecta ao Snowflake
    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )

    cursor = conn.cursor()

    # Lê o arquivo Parquet especificado
    df = pd.read_parquet(file_path)

    # Converte 'created_at' para string no formato ISO 8601
    df['created_at'] = df['created_at'].astype(str)

    # Insere os dados no Snowflake
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO tweets (tweet_id, created_at, text, user_id, user_name, screen_name, language)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            str(row['tweet_id']),
            row['created_at'],
            row['text'],
            str(row['user_id']),
            row['user_name'],
            row['screen_name'],
            row['language']
        ))

    cursor.close()
    conn.close()
    print("Dados carregados com sucesso no Snowflake.")
