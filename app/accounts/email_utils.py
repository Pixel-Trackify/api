import boto3
from django.conf import settings
from custom_admin.models import Configuration


def get_ses_client():
    return boto3.client(
        'ses',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_DEFAULT_REGION
    )


def send_register_email(to_email, user_name=None):
    config = Configuration.objects.first()
    email_body = config.email_register_subject if config and config.email_register_subject else "Bem-vindo(a)!"
    if user_name:
        email_body = email_body.replace("{{user_name}}", user_name)
    ses_client = get_ses_client()
    subject = "Bem-vindo(a) ao OneTrack"
    source_email = settings.AWS_SES_SOURCE_EMAIL
    response = ses_client.send_email(
        Source=source_email,
        Destination={'ToAddresses': [to_email]},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Html': {'Data': email_body}}
        }
    )
    return response


def send_password_reset_email(to_email, user_name, recovery_code):
    config = Configuration.objects.first()
    email_body = config.email_recovery_subject if config and config.email_recovery_subject else "Olá {{user_name}}, seu código de recuperação é: {{recovery_code}}"
    email_body = email_body.replace("{{user_name}}", user_name).replace(
        "{{recovery_code}}", recovery_code)
    ses_client = get_ses_client()
    subject = "Recuperação de Senha"
    source_email = settings.AWS_SES_SOURCE_EMAIL
    response = ses_client.send_email(
        Source=source_email,
        Destination={'ToAddresses': [to_email]},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Text': {'Data': email_body}}
        }
    )
    return response
