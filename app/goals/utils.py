import boto3
import uuid
import os
from datetime import datetime
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from django.conf import settings


def upload_to_s3(file, user, folder="support_attachments/"):
    """
    Faz o upload do arquivo para o Bucket S3 e retorna a URL pública.
    """
    # Inicializa o cliente S3
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_DEFAULT_REGION
    )

    # Verifica se as configurações do S3 estão presentes
    if not settings.AWS_BUCKET or not settings.AWS_DEFAULT_REGION:
        raise Exception("Configurações do AWS S3 estão ausentes ou inválidas.")

    # Gera um nome de arquivo único com base na data atual e UUID
    current_date = datetime.now().strftime("%Y%m%d%H%M%S")
    random_filename = f"{current_date}_{uuid.uuid4().hex}{os.path.splitext(file.name)[1]}"
    file_path = f"{folder}{user.uid}/{random_filename}"

    try:
        # Faz o upload do arquivo para o S3
        s3.upload_fileobj(
            file,
            settings.AWS_BUCKET,
            file_path,
            ExtraArgs={
                'ContentType': file.content_type,
                'ACL': 'public-read'
            }
        )
        # Retorna a URL pública do arquivo
        file_url = f"https://{settings.AWS_BUCKET}.s3.{settings.AWS_DEFAULT_REGION}.amazonaws.com/{file_path}"
        return file_url
    except (NoCredentialsError, PartialCredentialsError):
        raise Exception(
            "Erro de credenciais do AWS S3. Verifique as configurações.")
    except Exception as e:
        raise Exception(f"Erro ao fazer upload do arquivo: {str(e)}")
