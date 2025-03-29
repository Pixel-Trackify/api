from .models import Integration, IntegrationRequest, IntegrationSample
from .campaign_utils import recalculate_campaigns
from .campaign_operations import get_campaign_by_integration, update_campaign_fields, map_payment_status
import logging
from django.utils import timezone
import os
from decimal import Decimal

logger = logging.getLogger('django')


def process_sunize_webhook(data, integration):
    """
    Processa os dados do webhook do Sunize e atualiza as transações e requisições de integração.

    Args:
        data (dict): Dados recebidos do webhook do Sunize.
        integration (Integration): Instância da integração associada.

    Raises:
        ValueError: Se algum campo obrigatório estiver ausente nos dados recebidos.
    """
    try:
        # Verifica se já existe uma amostra para o gateway
        gateway = 'Sunize'
        if not IntegrationSample.objects.filter(gateway=gateway).exists():
            IntegrationSample.objects.create(gateway=gateway, response=data)

        # Extrai os dados necessários do payload do webhook
        event = data.get('event')
        body = data.get('body', {})
        transaction_id = body.get('order_id')
        status = map_payment_status(event, gateway)
        payment_method = body.get('payment_method')
        amount = sum(Decimal(commission.get('amount', 0))
                     for commission in body.get('Commissions', []))
        customer = body.get('Customer', {})
        response = data

        # Verifica se todos os campos obrigatórios estão presentes
        if not transaction_id or not status or not payment_method or amount is None:
            raise ValueError("Missing required fields in the webhook payload")

        if status == 'UNKNOWN':
            raise ValueError(f"Unknown status received: {status}")

        # Obtém a campanha associada à integração
        campaign = get_campaign_by_integration(integration)
        if not campaign:
            raise ValueError(
                f"No campaign associated with integration: {integration.id}")

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
            logger.error(
                f"Erro ao processar o webhook do Sunize: {e}", exc_info=True)
        raise
