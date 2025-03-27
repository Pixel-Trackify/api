from .models import Integration, IntegrationRequest, Transaction, IntegrationSample
from .campaign_utils import recalculate_campaigns
from .campaign_operations import get_campaign_by_integration, update_campaign_fields, map_payment_status
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


def process_disrupty_webhook(data, integration):
    """
    Processa os dados do webhook do Disrupty e atualiza as transações e requisições de integração.

    Args:
        data (dict): Dados recebidos do webhook do Disrupty.
        integration (Integration): Instância da integração associada.

    Raises:
        ValueError: Se algum campo obrigatório estiver ausente nos dados recebidos.
    """
    try:
        # Verifica se já existe uma amostra para o gateway
        gateway = 'Disrupty'
        if not IntegrationSample.objects.filter(gateway=gateway).exists():
            IntegrationSample.objects.create(gateway=gateway, response=data)

        # Extrai os dados necessários do payload do webhook
        transaction_id = data.get('hash')
        status = map_payment_status(data.get('payment_status'), 'Disrupty')
        payment_method = data.get('payment_method')
        amount = data.get('amount')
        customer = data.get('customer', {})
        response = data

        # Verifica se todos os campos obrigatórios estão presentes
        if not transaction_id or not status or not payment_method or not amount:
            raise ValueError("Missing required fields")

        # Cria um registro de requisição de integração
        IntegrationRequest.objects.create(
            integration=integration,
            status=status,
            payment_id=transaction_id,
            payment_method=payment_method,
            amount=amount,
            phone=customer.get('phone_number'),
            name=customer.get('name'),
            email=customer.get('email'),
            response=response,
            created_at=data.get('created_at', timezone.now()),
            updated_at=data.get('updated_at', timezone.now())
        )

        # Obtém a campanha associada à integração
        campaign = get_campaign_by_integration(integration)

        # Atualiza os campos da campanha com base no status
        update_campaign_fields(campaign, status, amount, gateway)

        # Recalcula os lucros e ROI da campanha
        recalculate_campaigns(campaign, campaign.total_ads,
                              campaign.amount_approved)

    except Exception as e:
        logger.error(f"Error processing transaction: {e}", exc_info=True)
        raise
