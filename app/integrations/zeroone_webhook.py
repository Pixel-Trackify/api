from .models import Integration, IntegrationRequest, Transaction, IntegrationSample
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
    try:
        # Verifica se já existe uma amostra para o gateway
        gateway = 'ZeroOne'
        if not IntegrationSample.objects.filter(gateway=gateway).exists():
            IntegrationSample.objects.create(gateway=gateway, response=data)

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

        amount = Decimal(amount) / 100  # Converte o valor de centavos para real
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
        # PEGAR A CAMPANHA
        # EXECUTAR ESSA SQL OU O MODEL DO DJANGO
        """
        select campaigns.* from integrations 
        inner join
            campaigns_integrations on campaigns_integrations.integration_id = integrations.id
        inner join 
            campaigns on campaigns.id = campaigns_integrations.campaign_id 
        where integrations.uid = '06636a1c-e3bc-4868-a385-2f023dc8d052'
        """
        # campain = SQL DE CIMA;
        """
        
        if status == 'APPROVED':
            campain.total_approved += 1
            campain.amount_approved += amount
         
        if status == 'PENDING':
            campain.total_pending += 1
            campain.amount_pending += amount
            
        campain.save()
        
        RECALCULAR PROFIT E ROI
        
        """
        
        
        # ATUALIZAR INFORMAÇÕES DESSA CAMPANHA
        # - total_approved
        # - total_pending
        # - amount_approved
        # - amount_pending 
        

        # Recalcula as campanhas associadas à integração
        recalculate_campaigns(integration)

    except Exception as e:
        logger.error(f"Error processing ZeroOne webhook: {e}", exc_info=True)
        raise
