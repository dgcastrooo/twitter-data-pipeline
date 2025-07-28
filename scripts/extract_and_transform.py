import os
import logging
import pandas as pd
import tweepy
from bs4 import BeautifulSoup
from dotenv import load_dotenv

def extract_and_transform():
    logging.basicConfig(level=logging.INFO)
    # Carrega variáveis do .env local
    load_dotenv()
    
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        raise ValueError("Variável de ambiente TWITTER_BEARER_TOKEN não está definida.")

    client = tweepy.Client(bearer_token=bearer_token)

    # Busca por tweets com a palavra-chave, em português, ignorando retweets
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

    users = {user.id: user for user in response.includes["users"]}

    data = []
    for tweet in response.data:
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

    # Remove qualquer HTML presente nos tweets usando BeautifulSoup
    def clean_text_with_bs(text):
        return BeautifulSoup(text, "html.parser").get_text(strip=True)

    df["text"] = df["text"].apply(clean_text_with_bs)

    # Salva o DataFrame como arquivo Parquet
    output_path = "/opt/airflow/data/tweets_clean.parquet"
    df.to_parquet(output_path, index=False)
    logging.info(f"Arquivo Parquet salvo com sucesso em: {output_path}")
