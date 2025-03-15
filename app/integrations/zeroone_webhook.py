from .models import Integration, IntegrationRequest, Transaction
from .campaign_utils import recalculate_campaigns, map_payment_status 
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


def process_zeroone_webhook(data, integration):
    """
    Processa os dados do webhook do ZeroOne e atualiza as transações e requisições de integração.

    Args:
        data (dict): Dados recebidos do webhook do ZeroOne.
        integration (Integration): Instância da integração associada.

    Raises:
        ValueError: Se algum campo obrigatório estiver ausente nos dados recebidos.
    """
    # Extrai os dados necessários do payload do webhook
    payment_id = data.get('paymentId')
    status = map_payment_status(data.get('status'), 'ZeroOne')
    payment_method = data.get('paymentMethod')
    amount = data.get('totalValue')
    customer = data.get('customer', {})
    response = data

    # Verifica se todos os campos obrigatórios estão presentes
    if not payment_id or not status or not payment_method or not amount:
        raise ValueError("Missing required fields")

    # Atualiza ou cria a transação com base no payment_id
    transaction, created = Transaction.objects.update_or_create(
        transaction_id=payment_id,
        defaults={
            'integration': integration,
            'status': status,
            'amount': amount,
            'method': payment_method,
            'data_response': response,
            'created_at': data.get('createdAt', timezone.now()),
            'updated_at': data.get('updatedAt', timezone.now())
        }
    )

    # Cria um registro de requisição de integração
    IntegrationRequest.objects.create(
        integration=integration,
        status=status,
        payment_id=payment_id,
        payment_method=payment_method,
        amount=amount,
        phone=customer.get('phone'),
        name=customer.get('name'),
        email=customer.get('email'),
        response=response,
        created_at=data.get('createdAt', timezone.now()),
        updated_at=data.get('updatedAt', timezone.now())
    )

    # Recalcula as campanhas associadas à integração
    recalculate_campaigns(integration)


