from campaigns.models import Campaign
from django.db.models import Sum
from integrations.models import Transaction


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
