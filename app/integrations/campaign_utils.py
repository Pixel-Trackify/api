from campaigns.models import Campaign
from django.db.models import Sum
from integrations.models import IntegrationRequest
from decimal import Decimal


def map_payment_status(status, gateway):
    """
    Mapeia os status de pagamento específicos para categorias mais gerais.

    Args:
        status (str): Status de pagamento específico.
        gateway (str): Nome do gateway de pagamento.

    Returns:
        str: Categoria geral do status de pagamento.
    """
    status_mapping = {
        'CloudFy': {
            'APPROVED': 'APPROVED',
            'PENDING': 'PENDING',
            'REFUSED': 'REJECTED',
            'REFUNDED': 'REFUNDED',
            'CHARGED_BACK': 'CHARGEBACK'
        },
        'VegaCheckout': {
            'approved': 'APPROVED',
            'pending': 'PENDING',
            'refused': 'REJECTED',
            'charge_back': 'CHARGEBACK',
            'refunded': 'REFUNDED',
            'expired': 'PENDING',
            'in_process': 'PENDING',
            'in_dispute': 'PENDING'
        },
        'Disrupty': {
            'processing': 'PENDING',
            'authorized': 'PENDING',
            'paid': 'APPROVED',
            'refunded': 'REFUNDED',
            'waiting_payment': 'PENDING',
            'refused': 'REJECTED',
            'antifraud': 'REJECTED',
            'chargedback': 'CHARGEBACK'
        },
        'WolfPay': {
            'processing': 'PENDING',
            'authorized': 'PENDING',
            'paid': 'APPROVED',
            'refunded': 'REFUNDED',
            'waiting_payment': 'PENDING',
            'refused': 'REJECTED',
            'antifraud': 'REJECTED',
            'chargedback': 'CHARGEBACK'
        },
        'ParadisePag': {
            'PENDING': 'PENDING',
            'APPROVED': 'APPROVED',
            'REJECTED': 'REJECTED',
            'REFUNDED': 'REFUNDED',
            'CHARGEBACK': 'CHARGEBACK'
        },
        'ZeroOne': {
            'PENDING': 'PENDING',
            'APPROVED': 'APPROVED',
            'REJECTED': 'REJECTED',
            'REFUNDED': 'REFUNDED',
            'CHARGEBACK': 'CHARGEBACK'
        },
        'WestPay': {
            'waiting_payment': 'PENDING',
            'paid': 'APPROVED',
            'refused': 'REJECTED',
            'canceled': 'REJECTED',
            'expired': 'PENDING',
            'refunded': 'REFUNDED',
            'chargedback': 'CHARGEBACK',
            'in_protest': 'CHARGEBACK'
        },
        'TriboPay': {
            'processing': 'PENDING',
            'authorized': 'PENDING',
            'paid': 'APPROVED',
            'refunded': 'REFUNDED',
            'waiting_payment': 'PENDING',
            'refused': 'REJECTED',
            'antifraud': 'REJECTED',
            'chargedback': 'CHARGEBACK'
        },
        'Sunize': {
            "SALE_APPROVED": "approved",
            "PIX_GENERATED": "pending",
            "SALE_REFUND": "refunded",
            "SALE_REJECTED": "rejected",
            "ABANDONED_CART": "abandoned",
            "BANK_SLIP_GENERATED": "pending"
        }
    }
    return status_mapping.get(gateway, {}).get(status, 'UNKNOWN')


def recalculate_campaigns(integration):
    """
    Recalcula as informações das campanhas associadas à integração.

    Args:
        integration (Integration): Instância da integração associada.
    """
    # Obtém todas as campanhas associadas à integração
    campaigns = Campaign.objects.filter(integrations=integration)
    for campaign in campaigns:
        # Obtém todas as requisições de integração associadas à integração
        integration_requests = IntegrationRequest.objects.filter(
            integration=integration)

        # Calcula os totais e valores das requisições aprovadas, pendentes, reembolsadas e chargeback
        total_approved = integration_requests.filter(status='APPROVED').count()
        total_pending = integration_requests.filter(status='PENDING').count()
        total_refunded = integration_requests.filter(status='REFUNDED').count()
        total_chargeback = integration_requests.filter(
            status='CHARGEBACK').count()

        amount_approved = integration_requests.filter(
            status='APPROVED').aggregate(Sum('amount'))['amount__sum'] or 0
        amount_pending = integration_requests.filter(status='PENDING').aggregate(
            Sum('amount'))['amount__sum'] or 0
        amount_refunded = integration_requests.filter(status='REFUNDED').aggregate(
            Sum('amount'))['amount__sum'] or 0
        amount_chargeback = integration_requests.filter(status='CHARGEBACK').aggregate(
            Sum('amount'))['amount__sum'] or 0

        # CPU é igual ao CPM
        price_unit = Decimal(campaign.CPM) / Decimal(1000)

        # Atualiza o total de anúncios somando o CPU
        campaign.total_ads += price_unit

        # Calcula o custo total com base no CPM e nas visualizações
        cost = campaign.total_views 

        # Calcula o lucro (profit) considerando o valor aprovado e o custo
        profit = amount_approved - cost - amount_refunded - amount_chargeback

        # Calcula o ROI (taxa de conversão)
        roi = (profit / amount_approved) * 100 if amount_approved > 0 else 0

        # Atualiza os campos da campanha com os novos valores calculados
        campaign.total_approved = total_approved
        campaign.total_pending = total_pending
        campaign.total_refunded = total_refunded
        campaign.total_chargeback = total_chargeback
        campaign.amount_approved = amount_approved
        campaign.amount_pending = amount_pending
        campaign.amount_refunded = amount_refunded
        campaign.amount_chargeback = amount_chargeback
        campaign.profit = profit  # Atualiza o lucro calculado
        campaign.ROI = roi  # Atualiza o ROI calculado
        campaign.save()
