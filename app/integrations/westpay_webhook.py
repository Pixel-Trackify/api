from .models import Integration, IntegrationRequest, IntegrationSample
from .campaign_utils import recalculate_campaigns
from .campaign_operations import get_campaign_by_integration, update_campaign_fields, map_payment_status
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def process_westpay_webhook(data, integration):
    """
    Processa os dados do webhook do WestPay e atualiza as requisições de integração.

    Args:
        data (dict): Dados recebidos do webhook do WestPay.
        integration (Integration): Instância da integração associada.

    Raises:
        ValueError: Se algum campo obrigatório estiver ausente nos dados recebidos.
    """
    try:
        # Verifica se já existe uma amostra para o gateway
        gateway = 'WestPay'
        if not IntegrationSample.objects.filter(gateway=gateway).exists():
            IntegrationSample.objects.create(gateway=gateway, response=data)

        # Extrai os dados necessários do payload do webhook
        transaction_data = data.get('data', {})
        transaction_id = transaction_data.get('id')
        status = transaction_data.get('status')
        payment_method = transaction_data.get('paymentMethod')
        amount = transaction_data.get('amount')
        customer = transaction_data.get('customer', {})
        response = data

        # Verifica se todos os campos obrigatórios estão presentes
        if not transaction_id or not status or not payment_method or not amount:
            raise ValueError("Missing required fields")

        logger.info(
            f"Attempting to update or create integration request with ID: {transaction_id}")

        # Mapeia o status específico do gateway para um status geral
        mapped_status = map_payment_status(status, 'WestPay')

        # Atualiza ou cria a requisição de integração com base no transaction_id
        integration_request, created = IntegrationRequest.objects.update_or_create(
            payment_id=transaction_id,
            defaults={
                'integration': integration,
                'status': mapped_status,
                'payment_method': payment_method,
                'amount': amount,
                'phone': customer.get('phone'),
                'name': customer.get('name'),
                'email': customer.get('email'),
                'response': response,
                'created_at': transaction_data.get('createdAt', timezone.now()),
                'updated_at': timezone.now()
            }
        )

        # Obtém a campanha associada à integração
        campaign = get_campaign_by_integration(integration)

        # Atualiza os campos da campanha com base no status
        update_campaign_fields(campaign, status, amount, gateway)

        # Recalcula os lucros e ROI da campanha
        recalculate_campaigns(integration)

        logger.info(
            f"Integration request {'created' if created else 'updated'}: {integration_request}")

    except Exception as e:
        logger.error(
            f"Error processing integration request: {e}", exc_info=True)
        raise
