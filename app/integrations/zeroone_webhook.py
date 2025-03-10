from .models import Integration, IntegrationRequest, Transaction
from campaigns.models import Campaign  
from django.db.models import Sum
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
    status = data.get('status')
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


def recalculate_campaigns(integration):
    """
    Recalcula as informações das campanhas associadas à integração.

    Args:
        integration (Integration): Instância da integração associada.
    """
    # Obtém todas as campanhas associadas à integração
    campaigns = Campaign.objects.filter(integrations=integration)
    for campaign in campaigns:
        # Obtém todas as transações associadas à integração
        transactions = Transaction.objects.filter(integration=integration)

        # Calcula os totais e valores das transações aprovadas e pendentes
        total_approved = transactions.filter(status='APPROVED').count()
        total_pending = transactions.filter(status='PENDING').count()
        amount_approved = transactions.filter(
            status='APPROVED').aggregate(Sum('amount'))['amount__sum'] or 0
        amount_pending = transactions.filter(status='PENDING').aggregate(
            Sum('amount'))['amount__sum'] or 0

        # Calcula o lucro e o ROI (taxa de conversão)
        profit = amount_approved - amount_pending
        roi = (profit / amount_approved) * 100 if amount_approved > 0 else 0

        # Atualiza os campos da campanha com os novos valores calculados
        campaign.total_approved = total_approved
        campaign.total_pending = total_pending
        campaign.amount_approved = amount_approved
        campaign.amount_pending = amount_pending
        campaign.profit = profit
        campaign.ROI = roi
        campaign.save()
