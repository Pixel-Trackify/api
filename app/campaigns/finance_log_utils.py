from django.utils.timezone import now
from decimal import Decimal
from .models import FinanceLogs


def update_finance_logs(campaign, old_status=None, old_amount=Decimal('0.0'), status=None, amount=Decimal('0.0')):
    """
    Atualiza ou cria um registro no FinanceLogs para o dia atual com base nos dados da Campaign.

    Args:
        campaign (Campaign): Instância da campanha cujos dados serão usados para atualizar o FinanceLogs.
        old_status (str): Status anterior da campanha (APPROVED, PENDING, etc.).
        old_amount (Decimal): Valor anterior associado ao status antigo.
        status (str): Novo status da campanha (APPROVED, PENDING, etc.).
        amount (Decimal): Novo valor associado ao novo status.

    Returns:
        FinanceLogs: O registro atualizado ou criado no FinanceLogs.
    """
    today = now().date()
    old_status = old_status if old_status else None
    old_amount = old_amount if old_amount else Decimal('0.0')
    # Decrementar os campos da campanha com base no status antigo 

    if old_status:
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

    # Incrementar os campos da campanha com base no novo status
    if status:
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

    # Calcula o profit e ROI
    profit = campaign.amount_approved - campaign.total_ads
    ROI = (profit / campaign.total_ads) * \
        100 if campaign.total_ads > 0 else Decimal('0.0')

    # Atualizar ou criar o registro no FinanceLogs
    finance_log, created = FinanceLogs.objects.update_or_create(
        campaign=campaign,
        date=today,
        defaults={
            'profit': profit,
            'ROI': ROI,
            'total_views': campaign.total_views,
            'total_clicks': campaign.total_clicks,
            'total_ads': campaign.total_ads,
            'total_approved': campaign.total_approved,
            'total_pending': campaign.total_pending,
            'total_refunded': campaign.total_refunded,
            'total_abandoned': campaign.total_abandoned,
            'total_chargeback': campaign.total_chargeback,
            'total_rejected': campaign.total_rejected,
            'amount_approved': campaign.amount_approved,
            'amount_pending': campaign.amount_pending,
            'amount_refunded': campaign.amount_refunded,
            'amount_rejected': campaign.amount_rejected,
            'amount_chargeback': campaign.amount_chargeback,
            'amount_abandoned': campaign.amount_abandoned,
        }
    )

    return finance_log
