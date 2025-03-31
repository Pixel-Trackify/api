from .models import Integration, IntegrationRequest, Transaction, IntegrationSample
from .campaign_utils import recalculate_campaigns
from .campaign_operations import get_campaign_by_integration, update_campaign_fields, map_payment_status
import logging
from django.utils import timezone
from decimal import Decimal
import os

logger = logging.getLogger('django')


def process_vega_checkout_webhook(data, integration):
    """
    Processa os dados do webhook do Vega Checkout e atualiza as transações e requisições de integração.

    Args:
        data (dict): Dados recebidos do webhook do Vega Checkout.
        integration (Integration): Instância da integração associada.

    Raises:
        ValueError: Se algum campo obrigatório estiver ausente nos dados recebidos.
    """
    try:
        # Verifica se já existe uma amostra para o gateway
        gateway = 'VegaCheckout'
        if not IntegrationSample.objects.filter(gateway=gateway).exists():
            IntegrationSample.objects.create(gateway=gateway, response=data)

        # Extrai os dados necessários do payload do webhook
        transaction_id = data.get('transaction_token')
        status = map_payment_status(data.get('status'), 'VegaCheckout')
        payment_method = data.get('method')
        amount = int(data.get('total_price'))
        customer = data.get('customer', {})
        response = data

        # Verifica se todos os campos obrigatórios estão presentes
        if not transaction_id or not status or not payment_method or not amount:
            raise ValueError("Missing required fields")

        if status == 'UNKNOWN':
            raise ValueError(f"Unknown status received: {status}")

        # Obtém a campanha associada à integração
        campaign = get_campaign_by_integration(integration)
        if not campaign:
            raise ValueError(
                f"No campaign associated with integration: {integration.id}")

        # Converte o valor de centavos para real
        amount = Decimal(amount) / 100
        # Cria um registro de requisição de integração
        integration_request, created = IntegrationRequest.objects.update_or_create(
            integration=integration,
            status=status,
            payment_id=transaction_id,
            payment_method=payment_method,
            amount=amount,
            phone=customer.get('phone'),
            name=customer.get('name'),
            email=customer.get('email'),
            response=response,
            created_at=data.get('created_at', timezone.now()),
            updated_at=data.get('updated_at', timezone.now())
        )

        # Determina se foi um insert ou update
        operation_type = 'insert' if created else 'update'

        # Atualiza os campos da campanha com base no status
        update_campaign_fields(
            integration_request, operation_type, campaign, status, amount, gateway)

        # Recalcula os lucros e ROI da campanha
        recalculate_campaigns(campaign, campaign.total_ads,
                              campaign.amount_approved)
    except Exception as e:
        if bool(int(os.getenv('DEBUG', 0))):
            logger.error(f"Error processing transaction: {e}", exc_info=True)

        raise
