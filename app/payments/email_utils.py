import boto3
from django.conf import settings
from custom_admin.models import Configuration
from datetime import datetime
import os
import logging

logger = logging.getLogger('django')

def get_ses_client():
    return boto3.client('ses',
                        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                        region_name=settings.AWS_DEFAULT_REGION)


def send_subscription_paid_email(to_email, total_paid=None, user_name=None):
    config = Configuration.objects.first()
    email_subject = config.email_subscription_paid_subject if config else None
    email_body = config.email_subscription_paid if config else None
     
    if not email_subject or not email_body:
        logger.error("Email subject or body not configured in Configuration model.")
        return None
    
    # Substituições no template
    now = datetime.now()
    email_body = (
        email_body
        .replace("{{ano_atual}}", str(now.year))
        .replace("{{link_dashboard}}",
                 os.environ.get('PAINEL_URL', 'https://painel.onetracking.io/') + "pagamentos")
        .replace("{{data_pagamento}}", now.strftime("%d/%m/%Y"))
    )
    if user_name:
        email_body = email_body.replace("{{user_name}}", user_name)
    if total_paid is not None:
        email_body = email_body.replace("{{valor_pago}}", f"{total_paid:.2f}")
            
    ses_client = get_ses_client()
    source_email = settings.AWS_SES_SOURCE_EMAIL
    
    try:
        response = ses_client.send_email(
            Source=source_email,
            Destination={'ToAddresses': [to_email]},
            Message={
                'Subject': {'Data': email_subject},
                'Body': {'Html': {'Data': email_body}}
            }
        )
        return response
    except Exception as e:
        logger.exception(f"[send_subscription_paid_email] falha ao enviar email para {to_email}")
        logger.error(f"Erro ao enviar email: {e}")
        return None
    


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
