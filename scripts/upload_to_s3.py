import boto3  # SDK da AWS para interagir com o S3
import logging  # Para registrar mensagens de log
import os  # Para verificar existência do arquivo local

def upload_to_s3(file_path, bucket_name, s3_key):  # Função que envia um arquivo local para o bucket S3
    if not os.path.exists(file_path):  # Verifica se o arquivo existe antes de tentar enviar
        logging.error(f"❌ Arquivo não encontrado: {file_path}")  # Loga erro se o arquivo não for encontrado
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")  # Lança exceção para interromper a DAG

    try:
        s3 = boto3.client('s3')  # Cria cliente do S3 com base nas credenciais de ambiente
        s3.upload_file(file_path, bucket_name, s3_key)  # Envia o arquivo para o bucket com a chave especificada
        logging.info(f"✅ Upload feito com sucesso: s3://{bucket_name}/{s3_key}")  # Loga sucesso do upload
    except Exception as e:  # Captura qualquer erro que acontecer
        logging.error(f"❌ Erro no upload: {str(e)}")  # Loga o erro com mensagem
        raise  # Repassa o erro para o Airflow registrar como falha
