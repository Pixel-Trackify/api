from datetime import timedelta, datetime
from collections import defaultdict
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from django.utils.timezone import now
from django.db.models import Sum, Count, Q, Value
from django.db.models.functions import TruncDate
from .permissions import IsSuperUser
from accounts.models import Usuario
from campaigns.models import FinanceLogs
from .serializers import DashboardSerializer, UsuarioSerializer
from .schemas import admin_dashboard_schema
from django.db import models


class AdminDashboardViewSet(ViewSet):
    permission_classes = [IsSuperUser]

    def get_date_range(self, start, end):
        """Calcula o intervalo de datas com base nos parâmetros fornecidos."""
        if not start and not end:
            end_date = now().date()
            start_date = end_date - timedelta(days=30)
        elif start and not end:
            start_date = end_date = datetime.strptime(start, '%Y-%m-%d').date()
        else:
            start_date = datetime.strptime(start, '%Y-%m-%d').date()
            end_date = datetime.strptime(end, '%Y-%m-%d').date()
        return start_date, end_date

    def get_register_stats(self, start_date, end_date):
        """Obtém estatísticas de registros de usuários (REGISTER)."""
        return Usuario.objects.filter(
            date_joined__range=[start_date, end_date]
        ).annotate(
            type=Value("REGISTER", output_field=models.CharField()),
            value=Count('uid'),
            date=TruncDate('date_joined')
        ).values('type', 'value', 'date')

    def get_subscription_stats(self, start_date, end_date):
        """Obtém estatísticas de assinaturas ativas (SUBSCRIPTION)."""
        return Usuario.objects.filter(
            date_joined__range=[start_date, end_date]
        ).annotate(
            type=Value("SUBSCRIPTION", output_field=models.CharField()),
            value=Count('uid', filter=Q(subscription_active=True)),
            date=TruncDate('date_joined')
        ).values('type', 'value', 'date')

    def fill_missing_days(self, users, start_date, end_date):
        """Preenche os dias ausentes no intervalo de datas com valores 0."""
        user_data = defaultdict(lambda: defaultdict(int))
        for user in users:
            user_data[user['type']][user['date']] = user['value']

        return [
            {
                "type": user_type,
                "value": user_data[user_type].get(date, 0),
                "date": date
            }
            for date in (start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1))
            for user_type in ['REGISTER', 'SUBSCRIPTION']
        ]

    def get_finance_stats(self, finance_logs):
        """Calcula estatísticas financeiras agregadas."""
        return {
            "total_approved": finance_logs.aggregate(total=Sum('total_approved'))['total'] or 0,
            "total_pending": finance_logs.aggregate(total=Sum('total_pending'))['total'] or 0,
            "total_refunded": finance_logs.aggregate(total=Sum('total_refunded'))['total'] or 0,
            "total_abandoned": finance_logs.aggregate(total=Sum('total_abandoned'))['total'] or 0,
            "total_chargeback": finance_logs.aggregate(total=Sum('total_chargeback'))['total'] or 0,
            "total_rejected": finance_logs.aggregate(total=Sum('total_rejected'))['total'] or 0,
            "amount_approved": finance_logs.aggregate(total=Sum('amount_approved'))['total'] or 0,
            "amount_pending": finance_logs.aggregate(total=Sum('amount_pending'))['total'] or 0,
            "amount_refunded": finance_logs.aggregate(total=Sum('amount_refunded'))['total'] or 0,
            "amount_rejected": finance_logs.aggregate(total=Sum('amount_rejected'))['total'] or 0,
            "amount_chargeback": finance_logs.aggregate(total=Sum('amount_chargeback'))['total'] or 0,
            "amount_abandoned": finance_logs.aggregate(total=Sum('amount_abandoned'))['total'] or 0,
            "total_ads": finance_logs.aggregate(total=Sum('total_ads'))['total'] or 0,
            "profit": finance_logs.aggregate(total=Sum('profit'))['total'] or 0,
            "total_views": finance_logs.aggregate(total=Sum('total_views'))['total'] or 0,
            "total_clicks": finance_logs.aggregate(total=Sum('total_clicks'))['total'] or 0,
            "stats": {
                "PIX": finance_logs.aggregate(pix_amount=Sum('pix_amount')).get('pix_amount', 0) or 0,
                "CARD_CREDIT": finance_logs.aggregate(credit_card_amount=Sum('credit_card_amount')).get('credit_card_amount', 0) or 0,
                "DEBIT_CARD": finance_logs.aggregate(debit_card_amount=Sum('debit_card_amount')).get('debit_card_amount', 0) or 0,
                "BOLETO": finance_logs.aggregate(boleto_amount=Sum('boleto_amount')).get('boleto_amount', 0) or 0,
            },
        }

    @admin_dashboard_schema
    def list(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        user = request.query_params.get('user')

        # Obter intervalo de datas
        start_date, end_date = self.get_date_range(start, end)

        finance_logs = FinanceLogs.objects.filter(
            campaign__created_at__range=[start_date, end_date]
        )
        if user:
            finance_logs = finance_logs.filter(campaign__user__uid=user)

        # Obter estatísticas de usuários
        total_users = Usuario.objects.filter(
            date_joined__range=[start_date, end_date]).count()
        total_users_subscription = Usuario.objects.filter(
            subscription_active=True).count()

        # Obter estatísticas de REGISTER e SUBSCRIPTION
        register_stats = self.get_register_stats(start_date, end_date)
        subscription_stats = self.get_subscription_stats(start_date, end_date)
        users = list(register_stats) + list(subscription_stats)
        filled_users = self.fill_missing_days(users, start_date, end_date)

        finance_stats = self.get_finance_stats(finance_logs)

        top_users = Usuario.objects.order_by('-profit')[:10]

        response_data = {
            "total_users": total_users,
            "total_users_subscription": total_users_subscription,
            **finance_stats,
            "users": filled_users,
            "top_users": UsuarioSerializer(top_users, many=True).data,
        }

        serializer = DashboardSerializer(response_data)
        return Response(serializer.data)
