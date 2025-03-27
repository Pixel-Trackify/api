import logging
from campaigns.models import Campaign

logger = logging.getLogger(__name__)


def map_payment_status(status, gateway):
    """
    Mapeia o status do pagamento para o status interno do sistema.

    Args:
        status (str): Status do pagamento recebido.
        gateway (str): Nome do gateway de pagamento.

    Returns:
        str: Status mapeado para o sistema interno.
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
            "SALE_APPROVED": "APPROVED",
            "PIX_GENERATED": "PENDING",
            "SALE_REFUND": "refunded",
            "SALE_REJECTED": "rejected",
            "ABANDONED_CART": "abandoned",
            "BANK_SLIP_GENERATED": "pending"
        }
    }

    return status_mapping.get(gateway, {}).get(status, 'UNKNOWN')


def get_campaign_by_integration(integration):
    """
    Obtém a campanha associada à integração.

    Args:
        integration (Integration): Instância da integração associada.

    Returns:
        Campaign: A campanha associada à integração.

    Raises:
        ValueError: Se nenhuma campanha for encontrada.
    """
    campaign = Campaign.objects.filter(integrations=integration).first()
    if not campaign:
        raise ValueError("Nenhuma campanha associada à integração encontrada.")
    return campaign


def update_campaign_fields(campaign, status, amount, gateway):
    """
    Atualiza os campos da campanha com base no status e no valor.

    Args:
        campaign (Campaign): Instância da campanha a ser atualizada.
        status (str): Status da transação (APPROVED, PENDING, etc.).
        amount (Decimal): Valor da transação.
        gateway (str): Nome do gateway de pagamento.

    Returns:
        None
    """
    try:
        # Mapeia o status recebido para o status interno do sistema
        mapped_status = map_payment_status(status, gateway)

        # Atualiza os campos da campanha com base no status mapeado
        if mapped_status == 'APPROVED':
            campaign.total_approved += 1
            campaign.amount_approved += amount

        elif mapped_status == 'PENDING':
            campaign.total_pending += 1
            campaign.amount_pending += amount

        # Salva as alterações na campanha
        campaign.save()

    except Exception as e:
        logger.error(
            f"Erro ao atualizar os campos da campanha: {e}", exc_info=True)
        raise
