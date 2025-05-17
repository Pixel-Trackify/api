from campaigns.models import FinanceLogs
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta


def get_financial_data(user=None, kwai=None, start_date=None, end_date=None):
    """
    Retorna os dados financeiros agregados e overviews para um usuário ou uma conta Kwai.
    """
    # Define o intervalo padrão de 30 dias se as datas não forem fornecidas
    if not start_date and not end_date:
        today = timezone.now().date()
        start_date = today - timedelta(days=30)
        end_date = today

    # Filtrar despesas e receitas (FinanceLogs)
    if user:
        finance_logs = FinanceLogs.objects.filter(
            campaign__user=user,
            date__gte=start_date,
            date__lte=end_date
        )
    elif kwai:
        finance_logs = FinanceLogs.objects.filter(
            campaign__kwai_campaigns__kwai=kwai,
            date__gte=start_date,
            date__lte=end_date
        )
    else:
        raise ValueError("É necessário fornecer um 'user' ou 'kwai'.")

    # Agregações principais
    total_ads = finance_logs.aggregate(total_ads=Sum('total_ads'))[
        'total_ads'] or 0
    total_views = finance_logs.aggregate(total_views=Sum('total_views'))[
        'total_views'] or 0
    total_clicks = finance_logs.aggregate(total_clicks=Sum('total_clicks'))[
        'total_clicks'] or 0
    total_approved = finance_logs.aggregate(total_approved=Sum('total_approved'))[
        'total_approved'] or 0
    total_pending = finance_logs.aggregate(total_pending=Sum('total_pending'))[
        'total_pending'] or 0
    total_refunded = finance_logs.aggregate(total_refunded=Sum('total_refunded'))[
        'total_refunded'] or 0
    total_abandoned = finance_logs.aggregate(total_abandoned=Sum('total_abandoned'))[
        'total_abandoned'] or 0
    total_chargeback = finance_logs.aggregate(
        total_chargeback=Sum('total_chargeback'))['total_chargeback'] or 0
    total_rejected = finance_logs.aggregate(total_rejected=Sum('total_rejected'))[
        'total_rejected'] or 0

    # Valores monetários
    amount_approved = finance_logs.aggregate(amount_approved=Sum('amount_approved'))[
        'amount_approved'] or 0
    amount_pending = finance_logs.aggregate(amount_pending=Sum('amount_pending'))[
        'amount_pending'] or 0
    amount_refunded = finance_logs.aggregate(amount_refunded=Sum('amount_refunded'))[
        'amount_refunded'] or 0
    amount_rejected = finance_logs.aggregate(amount_rejected=Sum('amount_rejected'))[
        'amount_rejected'] or 0
    amount_chargeback = finance_logs.aggregate(
        amount_chargeback=Sum('amount_chargeback'))['amount_chargeback'] or 0
    amount_abandoned = finance_logs.aggregate(
        amount_abandoned=Sum('amount_abandoned'))['amount_abandoned'] or 0

    # Estatísticas de pagamento (stats)
    stats = {
        "PIX": finance_logs.aggregate(pix_amount=Sum('pix_amount'))['pix_amount'] or 0,
        "CARD_CREDIT": finance_logs.aggregate(credit_card_amount=Sum('credit_card_amount'))['credit_card_amount'] or 0,
        "DEBIT_CARD": finance_logs.aggregate(debit_card_amount=Sum('debit_card_amount'))['debit_card_amount'] or 0,
        "BOLETO": finance_logs.aggregate(boleto_amount=Sum('boleto_amount'))['boleto_amount'] or 0,
    }

    # Cálculo de lucro e ROI
    profit = amount_approved - total_ads
    roi = (profit / total_ads * 100) if total_ads > 0 else 0

    # Overviews (despesas e receitas por data)
    overviews = []

    # Adiciona as despesas (EXPENSE) ao overview
    expenses = finance_logs.values('date').annotate(
        total_expense=Sum('total_ads'))
    for expense in expenses:
        if 'total_expense' in expense and 'date' in expense:
            overviews.append({
                "type": "EXPENSE",
                "value": expense['total_expense'],
                "date": expense['date']
            })

    # Adiciona as receitas (REVENUE) ao overview
    revenues = finance_logs.values('date').annotate(
        total_revenue=Sum('amount_approved'))
    for revenue in revenues:
        if 'total_revenue' in revenue and 'date' in revenue:
            overviews.append({
                "type": "REVENUE",
                "value": revenue['total_revenue'],
                "date": revenue['date']
            })

    # Ordena os overviews por data
    overviews.sort(key=lambda x: x['date'])

    
    return {
        "source": "Kwai",
        "title": "zeroone pay",
        "CPM": "2.22",  
        "CPC": None,  
        "CPV": None,  
        "method": "CPM",  
        "total_approved": total_approved,
        "total_pending": total_pending,
        "amount_approved": round(amount_approved, 2),
        "amount_pending": round(amount_pending, 2),
        "total_abandoned": total_abandoned,
        "amount_abandoned": round(amount_abandoned, 2),
        "total_canceled": total_refunded + total_rejected + total_chargeback,
        "amount_canceled": round(amount_refunded + amount_rejected + amount_chargeback, 2),
        "total_refunded": total_refunded,
        "amount_refunded": round(amount_refunded, 2),
        "total_rejected": total_rejected,
        "amount_rejected": round(amount_rejected, 2),
        "total_chargeback": total_chargeback,
        "amount_chargeback": round(amount_chargeback, 2),
        "total_ads": round(total_ads, 8),
        "profit": round(profit, 5),
        "ROI": round(roi, 5),
        "total_views": total_views,
        "total_clicks": total_clicks,
        "created_at": finance_logs.earliest('date').date if finance_logs.exists() else None,
        "updated_at": finance_logs.latest('date').date if finance_logs.exists() else None,
        "stats": stats,
        "overviews": overviews,
    }
