from .models import Integration, IntegrationRequest, Transaction
from .campaign_utils import recalculate_campaigns
from campaigns.models import Campaign
from django.db.models import Sum
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

def process_cloudfy_webhook(data, integration):
    """
    Processa os dados do webhook do CloudFy e atualiza as transações e requisições de integração.

    Args:
        data (dict): Dados recebidos do webhook do CloudFy.
        integration (Integration): Instância da integração associada.

    Raises:
        ValueError: Se algum campo obrigatório estiver ausente nos dados recebidos.
    """
    try:
        # Extrai os dados necessários do payload do webhook
        payload = data.get('payload', {})
        transaction_id = payload.get('_id')
        status = payload.get('status')
        payment_method = payload.get('paymentMethod')
        amount = payload.get('value')
        customer = {
            'name': payload.get('payerName'),
            'cpf': payload.get('payerCpf'),
            'email': payload.get('payerEmail'),
            'phone': payload.get('payerPhone')
        }
        response = data

        # Verifica se todos os campos obrigatórios estão presentes
        if not transaction_id or not status or not payment_method or not amount:
            raise ValueError("Missing required fields")

        # Atualiza ou cria a transação com base no transaction_id
        transaction, created = Transaction.objects.update_or_create(
            transaction_id=transaction_id,
            defaults={
                'integration': integration,
                'status': status,
                'amount': amount,
                'method': payment_method,
                'data_response': response,
                'created_at': payload.get('createdAt', timezone.now()),
                'updated_at': payload.get('updatedAt', timezone.now())
            }
        )

        # Cria um registro de requisição de integração
        IntegrationRequest.objects.create(
            integration=integration,
            status=status,
            payment_id=transaction_id,  # Corrigir o nome do campo
            payment_method=payment_method,
            amount=amount,
            phone=customer.get('phone'),
            name=customer.get('name'),
            email=customer.get('email'),
            response=response,
            created_at=payload.get('createdAt', timezone.now()),
            updated_at=payload.get('updatedAt', timezone.now())
        )

        # Recalcula as campanhas associadas à integração
        recalculate_campaigns(integration)

    except Exception as e:
        logger.error(f"Error processing transaction: {e}", exc_info=True)
        raise

