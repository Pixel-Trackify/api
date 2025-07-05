import boto3
from django.conf import settings
from custom_admin.models import Configuration
from datetime import datetime
import os
import logging
from django.utils import timezone

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
            
    if bool(int(os.getenv('DEBUG', 0))):
        logger.error(f"DEBUG MODE: Enviando lembrete para {to_email}")
        logger.error(f"{email_subject}")
        logger.error(f"{email_body}")
        
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
    


def send_subscription_expired_email(to_email, expiration=None, user_name=None):
    config = Configuration.objects.first()
    email_subject = config.email_expired_subject if config else None
    email_body = config.email_expired if config else None
     
    if not email_subject or not email_body:
        logger.error("Email subject or body not configured in Configuration model.")
        return None
    
    # Substituições no template
    now = datetime.now()
    if expiration:
        if timezone.is_naive(expiration):
            expiration = timezone.make_aware(expiration, timezone.get_default_timezone())
        expiration_local = timezone.localtime(expiration, timezone.get_default_timezone())
        expiration_str = expiration_local.strftime("%d/%m/%Y")
    else:
        expiration_str = "N/A"
        
    email_body = (
        email_body
        .replace("{{ano_atual}}", str(now.year))
        .replace("{{link_pagamento}}",
                 os.environ.get('PAINEL_URL', 'https://painel.onetracking.io/') + "pagamentos")
        .replace("{{data_gerado}}", now.strftime("%d/%m/%Y"))
        .replace("{{data_expiracao}}", expiration_str)
    )
    
    if user_name:
        email_body = email_body.replace("{{user_name}}", user_name)
        
    if bool(int(os.getenv('DEBUG', 0))):
        logger.error(f"DEBUG MODE: Enviando marcar como expirado para {to_email}")
        logger.error(f"{email_subject}")
        logger.error(f"{email_body}")
    try:
        ses_client = get_ses_client()
        source_email = settings.AWS_SES_SOURCE_EMAIL
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
        logger.exception(f"[send_subscription_expired_email] falha ao enviar email para {to_email}")
        logger.error(f"Erro ao enviar email: {e}")
        return None
    
def send_subscription_reminder_email(to_email, expiration=None, user_name=None):
    config = Configuration.objects.first()
    email_subject = config.email_reminder_subject if config else None
    email_body = config.email_reminder if config else None
     
    if not email_subject or not email_body:
        logger.error("Email subject or body not configured in Configuration model.")
        return None
    
    # Substituições no template
    now = datetime.now()
    if expiration:
        if timezone.is_naive(expiration):
            expiration = timezone.make_aware(expiration, timezone.get_default_timezone())
        expiration_local = timezone.localtime(expiration, timezone.get_default_timezone())
        expiration_str = expiration_local.strftime("%d/%m/%Y")
    else:
        expiration_str = "N/A"
        
    email_body = (
        email_body
        .replace("{{ano_atual}}", str(now.year))
        .replace("{{link_pagamento}}",
                 os.environ.get('PAINEL_URL', 'https://painel.onetracking.io/') + "pagamentos")
        .replace("{{data_gerado}}", now.strftime("%d/%m/%Y"))
        .replace("{{data_expiracao}}", expiration_str)
    )
    
    if user_name:
        email_body = email_body.replace("{{user_name}}", user_name)
        
    if bool(int(os.getenv('DEBUG', 0))):
        logger.error(f"DEBUG MODE: Enviando lembrete para {to_email}")
        logger.error(f"{email_subject}")
        logger.error(f"{email_body}")
    try:
        ses_client = get_ses_client()
        source_email = settings.AWS_SES_SOURCE_EMAIL
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