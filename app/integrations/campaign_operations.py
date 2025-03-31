import logging
import os
from campaigns.models import Campaign

logger = logging.getLogger('django')


def map_payment_status(status, gateway):
    """
    Mapeia o status do pagamento para o status interno do sistema.

    Args:
        status (str): Status do pagamento recebido.
        gateway (str): Nome do gateway de pagamento.

    Returns:
        str: Status mapeado para o sistema interno.
    """
    # Precisa ter apenas esses 6 status
    """
    APPROVED: Vendas aprovada.
    PENDING: Vendas pendentes
    REFUNDED: Vendas reembolsadas.
    REJECTED: Vendas recusada.
    ABANDONED: Vendas cancelada ou abandonada.
    CHARGEBACK: Vendas contestadas
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
            'expired': 'ABANDONED',
            'in_process': 'PENDING',
            'in_dispute': 'CHARGEBACK'
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
            'canceled': 'ABANDONED',
            'expired': 'ABANDONED',
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
            "SALE_REFUND": "REFUNDED",
            "SALE_REJECTED": "REJECTED",
            "ABANDONED_CART": "ABANDONED",
            "BANK_SLIP_GENERATED": "PENDING"
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


def update_campaign_fields(integration, operation_type, campaign, status, amount, gateway):
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
    
    if bool(int(os.getenv('DEBUG', 0))):
        logger.info(f"Atualizando campos da campanha: {campaign.uid}, Status: {status}, Gateway: {gateway}")
        
    try:
        
        # Obter o status antigo da campanha
        old_status = integration.status
        old_amount = integration.amount
        
        # Decrementar os campos da campanha com base no status antigo (para evitar duplicação)
        if operation_type == 'update':
            if old_status == 'APPROVED':
                campaign.total_approved -= 1
                campaign.amount_approved -= old_amount

            if old_status == 'PENDING':
                campaign.total_pending -= 1
                campaign.amount_pending -= old_amount

            if old_status == 'REFUNDED':
                campaign.total_refunded -= 1
                campaign.amount_refunded -= old_amount

            if old_status == 'REJECTED':
                campaign.total_rejected -= 1
                campaign.amount_rejected -= old_amount

            if old_status == 'CHARGEBACK':
                campaign.total_chargeback -= 1
                campaign.amount_chargeback -= old_amount

            if old_status == 'ABANDONED':
                campaign.total_abandoned -= 1
                campaign.amount_abandoned -= old_amount
        
        # Incrementar os campos da campanha com base no status mapeado
        if status == 'APPROVED':
            campaign.total_approved += 1
            campaign.amount_approved += amount

        if status == 'PENDING':
            campaign.total_pending += 1
            campaign.amount_pending += amount
            
        if status == 'REFUNDED':
            campaign.total_refunded += 1
            campaign.amount_refunded += amount

        if status == 'REJECTED':
            campaign.total_rejected += 1
            campaign.amount_rejected += amount
            
        if status == 'CHARGEBACK':
            campaign.total_chargeback += 1
            campaign.amount_chargeback += amount
            
        if status == 'ABANDONED':
            campaign.total_abandoned += 1
            campaign.amount_abandoned += amount
        
        if status == 'CANCELED':
            campaign.total_canceled += 1
            campaign.amount_canceled += amount
            
        # Salva as alterações na campanha
        campaign.save()
    except Exception as e:
        logger.error(
            f"Erro ao atualizar os campos da campanha: {e}", exc_info=True)
        raise
