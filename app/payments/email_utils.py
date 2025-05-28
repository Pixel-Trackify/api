import boto3
from django.conf import settings
from custom_admin.models import Configuration


def send_subscription_paid_email(to_email, user_name=None):
    # Busca o corpo do e-mail no Configuration
    config = Configuration.objects.first()
    email_body = config.email_subscription_paid if config else "Pagamento confirmado com sucesso!"

    # Personalização opcional
    if user_name:
        email_body = email_body.replace("{{user_name}}", user_name)

    # Configurações do SES
    ses_client = boto3.client(
        'ses',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_DEFAULT_REGION
    )

    # Parâmetros do e-mail
    subject = "Pagamento confirmado"
    source_email = settings.AWS_SES_SOURCE_EMAIL

    response = ses_client.send_email(
        Source=source_email,
        Destination={'ToAddresses': [to_email]},
        Message={
            'Subject': {'Data': subject},
            'Body': {
                'Html': {'Data': email_body}
            }
        }
    )
    return response
