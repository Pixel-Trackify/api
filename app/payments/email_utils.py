import boto3
from django.conf import settings
from custom_admin.models import Configuration


def get_ses_client():
    return boto3.client('ses',
                        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                        region_name=settings.AWS_DEFAULT_REGION)


def send_subscription_paid_email(to_email, user_name=None):
    config = Configuration.objects.first()
    email_body = config.email_subscription_paid if config else "Pagamento confirmado com sucesso!"
    if user_name:
        email_body = email_body.replace("{{user_name}}", user_name)
    ses_client = get_ses_client()
    subject = "Pagamento confirmado"
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


def send_subscription_reminder_email(to_email, user_name=None):
    config = Configuration.objects.first()
    email_body = config.email_reminder if config else "Sua assinatura está prestes a expirar."
    if user_name:
        email_body = email_body.replace("{{user_name}}", user_name)
    ses_client = get_ses_client()
    subject = "Lembrete: sua assinatura vai expirar"
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
