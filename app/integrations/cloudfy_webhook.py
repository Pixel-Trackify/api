from .models import Integration, IntegrationRequest, Transaction, IntegrationSample
from .campaign_utils import recalculate_campaigns
from .campaign_operations import get_campaign_by_integration, update_campaign_fields, map_payment_status
import logging
from django.utils import timezone

logger = logging.getLogger('django')


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
        # Verifica se já existe uma amostra para o gateway
        gateway = 'CloudFy'
        if not IntegrationSample.objects.filter(gateway=gateway).exists():
            IntegrationSample.objects.create(gateway=gateway, response=data)
        # Extrai os dados necessários do payload do webhook
        payload = data.get('payload', {})
        transaction_id = payload.get('_id')
        status = map_payment_status(payload.get('status'), 'CloudFy')
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
        
        if status == 'UNKNOWN':
            raise ValueError(f"Unknown status received: {status}")
        
        # Obtém a campanha associada à integração
        campaign = get_campaign_by_integration(integration)
        if not campaign:
            raise ValueError(f"No campaign associated with integration: {integration.id}")
        
        # Cria um registro de requisição de integração
        integration_request, created = IntegrationRequest.objects.update_or_create(
            payment_id=transaction_id,
            defaults={
                'integration':integration,
                'status':status,
                'payment_id':transaction_id,  # Corrigir o nome do campo
                'payment_method':payment_method,
                'amount':amount,
                'phone':customer.get('phone'),
                'name':customer.get('name'),
                'email':customer.get('email'),
                'response':response,
                'created_at':payload.get('createdAt', timezone.now()),
                'updated_at':payload.get('updatedAt', timezone.now())
            }
        )

        # Determina se foi um insert ou update
        operation_type = 'insert' if created else 'update'
        
        # Atualiza os campos da campanha com base no status
        update_campaign_fields(integration_request, operation_type, campaign, status, amount, gateway)

        # Recalcula os lucros e ROI da campanha
        recalculate_campaigns(campaign, campaign.total_ads, campaign.amount_approved)
    except Exception as e:
        if bool(int(os.getenv('DEBUG', 0))):
            logger.error(f"Error processing transaction: {e}", exc_info=True)
        raise
