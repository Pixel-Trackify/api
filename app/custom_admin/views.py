from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.utils.timezone import now, timedelta
from .permissions import IsSuperUser
from accounts.models import Usuario
from campaigns.models import FinanceLogs
from .serializers import DashboardSerializer, UsuarioSerializer
from django.db.models import Sum, Count, Q, Value
from django.db.models.functions import TruncDate
from django.db import models
from .schemas import admin_dashboard_schema


class AdminDashboardViewSet(ViewSet):
    permission_classes = [IsSuperUser]

    @admin_dashboard_schema
    def list(self, request):

        start = request.query_params.get('start')
        end = request.query_params.get('end')
        user = request.query_params.get('user')

        # Calcular intervalo de datas
        if not start and not end:
            end_date = now()
            start_date = end_date - timedelta(days=30)
        elif start and not end:
            start_date = end_date = start
        else:
            start_date = start
            end_date = end

        finance_logs = FinanceLogs.objects.filter(
            campaign__created_at__range=[start_date, end_date]
        )
        if user:
            finance_logs = finance_logs.filter(campaign__user__uid=user)

        total_users = Usuario.objects.filter(
            date_joined__range=[start_date, end_date]
        ).count()
        total_users_subscription = Usuario.objects.filter(
            subscription_active=True
        ).count()
        total_approved = finance_logs.aggregate(
            total_approved=Sum('total_approved')
        )['total_approved'] or 0
        total_pending = finance_logs.aggregate(
            total_pending=Sum('total_pending')
        )['total_pending'] or 0
        total_refunded = finance_logs.aggregate(total_refunded=Sum('total_refunded'))[
            'total_refunded'] or 0
        total_abandoned = finance_logs.aggregate(total_abandoned=Sum('total_abandoned'))[
            'total_abandoned'] or 0
        total_chargeback = finance_logs.aggregate(
            total_chargeback=Sum('total_chargeback'))['total_chargeback'] or 0
        total_rejected = finance_logs.aggregate(total_rejected=Sum('total_rejected'))[
            'total_rejected'] or 0

        amount_approved = finance_logs.aggregate(
            amount_approved=Sum('amount_approved')
        )['amount_approved'] or 0
        amount_pending = finance_logs.aggregate(
            amount_pending=Sum('amount_pending')
        )['amount_pending'] or 0
        amount_refunded = finance_logs.aggregate(amount_refunded=Sum('amount_refunded'))[
            'amount_refunded'] or 0
        amount_rejected = finance_logs.aggregate(amount_rejected=Sum('amount_rejected'))[
            'amount_rejected'] or 0
        amount_chargeback = finance_logs.aggregate(
            amount_chargeback=Sum('amount_chargeback'))['amount_chargeback'] or 0
        amount_abandoned = finance_logs.aggregate(
            amount_abandoned=Sum('amount_abandoned'))['amount_abandoned'] or 0
        total_ads = finance_logs.aggregate(total_ads=Sum('total_ads'))[
            'total_ads'] or 0
        profit = finance_logs.aggregate(total=Sum('profit'))['total'] or 0
        total_views = finance_logs.aggregate(
            total=Sum('total_views')
        )['total'] or 0
        total_clicks = finance_logs.aggregate(
            total=Sum('total_clicks')
        )['total'] or 0

        stats = {
            "PIX": finance_logs.aggregate(pix_amount=Sum('pix_amount'))['pix_amount'] or 0,
            "CARD_CREDIT": finance_logs.aggregate(credit_card_amount=Sum('credit_card_amount'))['credit_card_amount'] or 0,
            "DEBIT_CARD": finance_logs.aggregate(debit_card_amount=Sum('debit_card_amount'))['debit_card_amount'] or 0,
            "BOLETO": finance_logs.aggregate(boleto_amount=Sum('boleto_amount'))['boleto_amount'] or 0,
        }

        register_stats = Usuario.objects.filter(
            date_joined__range=[start_date, end_date]
        ).annotate(

            type=Value("REGISTER", output_field=models.CharField()),
            value=Count('uid'),
            date=TruncDate('date_joined')
        ).values('type', 'value', 'date')

        subscription_stats = Usuario.objects.filter(
            date_joined__range=[start_date, end_date]
        ).annotate(

            type=Value("SUBSCRIPTION", output_field=models.CharField()),
            value=Count('uid', filter=Q(subscription_active=True)),
            date=TruncDate('date_joined')
        ).values('type', 'value', 'date')

        users = register_stats.union(subscription_stats)

        top_users = Usuario.objects.order_by('-profit')[:10]

        response_data = {
            "total_users": total_users,
            "total_users_subscription": total_users_subscription,
            "total_approved": total_approved,
            "total_pending": total_pending,
            "amount_approved": amount_approved,
            "amount_pending": amount_pending,
            "total_refunded": total_refunded,
            "total_abandoned": total_abandoned,
            "total_chargeback": total_chargeback,
            "total_rejected": total_rejected,
            "amount_refunded": amount_refunded,
            "amount_abandoned": amount_abandoned,
            "amount_chargeback": amount_chargeback,
            "amount_rejected": amount_rejected,
            "total_ads": total_ads,
            "profit": profit,
            "total_views": total_views,
            "total_clicks": total_clicks,
            "stats": stats,
            "users": list(users),
            "top_users": UsuarioSerializer(top_users, many=True).data,
        }

        serializer = DashboardSerializer(response_data)
        return Response(serializer.data)
