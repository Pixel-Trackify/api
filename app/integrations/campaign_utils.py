from campaigns.models import Campaign
from django.db.models import Sum
from integrations.models import IntegrationRequest
from decimal import Decimal
from integrations.campaign_operations import update_campaign_fields


def recalculate_campaigns(campaign, total_ads, amount_approved):
    """
    Recalcula o lucro (profit) e o ROI de uma campanha.

    Args:
        campaign (Campaign): Instância da campanha a ser atualizada.
        total_ads (Decimal): Custo total dos anúncios.
        amount_approved (Decimal): Valor total aprovado.

    Returns:
        None
    """
    # Calcula o lucro (profit)
    profit = Decimal(amount_approved) - Decimal(total_ads)

    # Calcula o ROI (taxa de retorno sobre investimento)
    roi = ((Decimal(amount_approved) - Decimal(total_ads)) / Decimal(total_ads)) * 100 if total_ads > 0 else 0

    # Atualiza os campos da campanha
    campaign.profit = profit
    campaign.ROI = roi

    # Opcional: Atualizar outros campos usando update_campaign_fields
    # update_campaign_fields(campaign, status, amount)  # Exemplo de uso, se necessário

    campaign.save()