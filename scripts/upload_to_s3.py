import boto3  # SDK da AWS
import logging  # Logs estruturados

def upload_to_s3(file_path, bucket_name, s3_key):
    s3 = boto3.client('s3')  # Cliente do S3
    try:
        s3.upload_file(file_path, bucket_name, s3_key)  # Envia o arquivo
        logging.info(f"✅ Upload feito com sucesso: s3://{bucket_name}/{s3_key}")
    except Exception as e:
        logging.error(f"❌ Erro no upload: {str(e)}")
        raise
