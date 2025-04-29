from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from campaigns.models import Campaign, FinanceLogs
from integrations.models import IntegrationRequest
from .models import KwaiCampaign
from .serializers import FinanceLogsSerializer
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, timedelta
from .schema import kwai_overview_schema


class KwaiOverview(APIView):
    """
     Endpoint para retornar os dados agregados dos últimos 30 dias da tabela FinanceLogs.
     """
    permission_classes = [permissions.IsAuthenticated]

    def get_overviews(self, user):
        """
        Função para calcular receitas (REVENUE) e despesas (EXPENSE) diárias.
        """

        today = timezone.now().date()
        start_date = today - timedelta(days=30)

        # Obter despesas diárias (EXPENSE)
        expenses = FinanceLogs.objects.filter(
            campaign__user=user,
            date__gte=start_date,
            date__lte=today
        ).values('date').annotate(
            total_expense=Sum('total_ads')
        )

        # Obter receitas diárias (REVENUE)
        integrations = IntegrationRequest.objects.filter(
            integration__user=user,
            status='APPROVED',
            created_at__gte=timezone.make_aware(
                datetime.combine(start_date, datetime.min.time())),
            created_at__lte=timezone.make_aware(
                datetime.combine(today, datetime.max.time()))
        ).values('created_at').annotate(
            total_revenue=Sum('amount')
        )

        # Combinar despesas e receitas
        overviews = []
        for expense in expenses:
            if 'total_expense' in expense and 'date' in expense:
                overviews.append({
                    "type": "EXPENSE",
                    "value": expense['total_expense'],
                    "date": expense['date']
                })
        for revenue in integrations:
            if 'total_revenue' in revenue and 'created_at' in revenue:
                overviews.append({
                    "type": "REVENUE",
                    "value": revenue['total_revenue'],
                    "date": revenue['created_at'].date()
                })

        # Ordenar por data
        overviews.sort(key=lambda x: x['date'])
        return overviews

    @kwai_overview_schema
    def get(self, request, *args, **kwargs):
        """
        Retorna os dados agregados e todos os registros de FinanceLogs dos últimos 30 dias.
        """
        today = timezone.now().date()
        start_date = today - timedelta(days=30)

        # Filtrar os registros de FinanceLogs dos últimos 30 dias
        finance_logs = FinanceLogs.objects.filter(
            campaign__user=request.user,
            date__gte=start_date
        )

        # Serializar os registros de FinanceLogs
        serializer = FinanceLogsSerializer(finance_logs, many=True)

        # Preparar os dados de stats
        stats = {
            "boleto": finance_logs.aggregate(Sum('boleto_total'))['boleto_total__sum'] or 0,
            "pix": finance_logs.aggregate(Sum('pix_total'))['pix_total__sum'] or 0,
            "credit_card": finance_logs.aggregate(Sum('credit_card_total'))['credit_card_total__sum'] or 0,
            "credit_debit": finance_logs.aggregate(Sum('debit_card_total'))['debit_card_total__sum'] or 0,
        }

        # Obter os overviews usando a função reutilizável
        overviews = self.get_overviews(request.user)

        # Montar a resposta
        response_data = {
            **(serializer.data[0] if serializer.data else {}),
            "stats": stats,
            "overviews": overviews,
        }

        return Response(response_data, status=status.HTTP_200_OK)
