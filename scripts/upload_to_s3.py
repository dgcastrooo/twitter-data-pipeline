import boto3
import logging
import os

def upload_to_s3(file_path, bucket_name, s3_key):
    # Verifica se o arquivo existe
    if not os.path.exists(file_path):
        logging.error(f"Arquivo não encontrado: {file_path}")
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    try:
        # Cria cliente do S3 e realiza o upload
        s3 = boto3.client('s3')
        s3.upload_file(file_path, bucket_name, s3_key)
        logging.info(f"Upload feito com sucesso: s3://{bucket_name}/{s3_key}")
    except Exception as e:
        # Registra e repassa o erro
        logging.error(f"Erro no upload: {str(e)}")
        raise
