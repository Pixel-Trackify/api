import requests
from django.conf import settings
import logging
from datetime import datetime
from accounts.models import User

logger = logging.getLogger(__name__)


logger = logging.getLogger(__name__)


def create_pix_payment(amount, cpf, idempotency_key, user, plan):
    url = f"{settings.FIRE_BANKING_API_URL}/payment"
    headers = {
        'apiKey': f"{settings.FIRE_BANKING_API_KEY}",
        'Content-Type': 'application/json',
        'Idempotency-Key': idempotency_key
    }
    
    try:
        user = User.objects.get(pk=user.pk)
    except User.DoesNotExist:
        logger.error(f"Usuário não encontrado: {user}")
        raise Exception(f"Usuário não encontrado: {user}")

    data = {
        "type": "PIX",
        "payer": {
            "fullName": user.name,
            "document": cpf
        },
        "transaction": {
            "value": int(amount * 100),  # Valor em centavos
            "description": f"- {plan.name}",
            "dueDate": datetime.now().strftime('%Y-%m-%d'),
            "externalId": idempotency_key
        }
    }
    try:
        logger.info(f"Enviando requisição para {url} com dados: {data} e headers: {headers}")
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        logger.info(f"Resposta da API do Fire Banking: {response_data}")
        return response_data
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao criar pagamento PIX: {e.response.text}")
        raise Exception(f"Erro ao criar pagamento PIX: {e.response.text}")


def check_pix_payment_status(transaction_id):
    url = f"{settings.FIRE_BANKING_API_URL}/payment/{transaction_id}"
    headers = {
        'Authorization': f"Bearer {settings.FIRE_BANKING_API_KEY}"
    }
    try:
        logger.info(
            f"Verificando status do pagamento para {url} com headers: {headers}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        logger.info(f"Resposta da API do Fire Banking: {response_data}")
        return response_data
    except requests.exceptions.RequestException as e:
        logger.error(
            f"Erro ao verificar status do pagamento PIX: {e.response.text}")
        raise Exception(
            f"Erro ao verificar status do pagamento PIX: {e.response.text}")
