from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from campaigns.models import Campaign, FinanceLogs
from integrations.models import IntegrationRequest
from .models import KwaiCampaign
from .serializers import FinanceLogsSerializer, KwaiSerializer, CampaignSerializer
from .models import Kwai, KwaiCampaign
from django.db.models import Sum
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from .schema import kwai_overview_schema
import logging
import uuid
from .schema import (
    kwai_list_view_get_schema,
    kwai_list_view_post_schema,
    kwai_detail_view_get_schema,
    kwai_detail_view_put_schema,
    kwai_detail_view_delete_schema,
    campaigns_not_in_use_view_get_schema


)


logger = logging.getLogger('django')


class KwaiViewSet(ModelViewSet):
    """
    ViewSet para gerenciar contas Kwai.
    """
    queryset = Kwai.objects.all()
    serializer_class = KwaiSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    @kwai_list_view_get_schema
    def list(self, request, *args, **kwargs):
        """
        Lista todas as contas Kwai.
        """
        return super().list(request, *args, **kwargs)

    @kwai_list_view_post_schema
    def create(self, request, *args, **kwargs):
        """
        Cria uma nova conta Kwai.
        """
        campaigns = request.data.get('campaigns', None)
        if not campaigns:
            return Response(
                {"error": "O campo 'campaigns' é obrigatório e não pode estar vazio."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @kwai_detail_view_get_schema
    def retrieve(self, request, pk=None, *args, **kwargs):
        """
        Retorna os detalhes de uma conta Kwai específica.
        """
        try:
            uuid.UUID(pk)
        except ValueError:
            return Response({"error": "UID inválido."}, status=status.HTTP_400_BAD_REQUEST)

        kwai = self.get_queryset().filter(uid=pk).first()
        if not kwai:
            return Response({"error": "Conta Kwai não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(kwai)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @kwai_detail_view_put_schema
    def update(self, request, pk=None, *args, **kwargs):
        """
        Atualiza os dados de uma conta Kwai específica, incluindo campanhas associadas.
        """
        kwai = self.get_queryset().filter(uid=pk).first()
        if not kwai:
            return Response({"error": "Conta Kwai não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        name = request.data.get('name', None)
        if name:
            kwai.name = name

        # Atualizar o campo 'campaigns'
        campaigns_data = request.data.get('campaigns', None)
        if campaigns_data:
            if not isinstance(campaigns_data, list):
                return Response(
                    {"error": "O campo 'campaigns' deve ser uma lista de objetos com 'uid'."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validar e associar campanhas
            campaign_uids = [campaign.get('uid')
                             for campaign in campaigns_data]
            campaigns = Campaign.objects.filter(uid__in=campaign_uids)

            if len(campaigns) != len(campaign_uids):
                return Response(
                    {"error": "Algumas campanhas fornecidas não foram encontradas."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Atualizar o campo 'in_use' das campanhas
            with transaction.atomic():

                kwai_campaigns = KwaiCampaign.objects.filter(kwai=kwai)
                for kwai_campaign in kwai_campaigns:
                    campaign = kwai_campaign.campaign
                    campaign.in_use = False
                    campaign.save()

                # Associar as novas campanhas e marcar como `in_use=True`
                KwaiCampaign.objects.filter(kwai=kwai).delete()
                for campaign in campaigns:
                    campaign.in_use = True
                    campaign.save()
                    KwaiCampaign.objects.create(kwai=kwai, campaign=campaign)

        kwai.save()

        serializer = self.get_serializer(kwai)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @kwai_detail_view_delete_schema
    def destroy(self, request, pk=None, *args, **kwargs):
        """
        Exclui uma conta Kwai específica.
        """
        if not request.user.is_superuser:
            return Response({"error": "Apenas administradores podem excluir contas."}, status=status.HTTP_403_FORBIDDEN)

        kwai = self.get_queryset().filter(uid=pk).first()
        if not kwai:
            return Response({"error": "Conta Kwai não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            kwai_campaigns = KwaiCampaign.objects.filter(kwai=kwai)
            for kwai_campaign in kwai_campaigns:
                campaign = kwai_campaign.campaign
                campaign.in_use = False
                campaign.save()

            kwai.delete()

        return Response({"message": "Conta Kwai excluída com sucesso."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='delete-multiple')
    def delete_multiple(self, request):
        """
        Permite que administradores excluam múltiplas contas Kwai de uma vez.
        - Recebe uma lista de UIDs no corpo da requisição.
        """
        if not request.user.is_superuser:
            return Response(
                {"error": "Apenas administradores podem excluir contas."},
                status=status.HTTP_403_FORBIDDEN
            )

        uids = request.data.get('uids', [])
        if not isinstance(uids, list) or not uids:
            return Response(
                {"error": "Nenhum UUID fornecido ou formato inválido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        invalid_uids = []
        with transaction.atomic():
            for uid in uids:
                try:
                    uuid.UUID(uid)
                except ValueError:
                    invalid_uids.append(uid)
                    continue

                kwai = Kwai.objects.filter(uid=uid).first()
                if kwai:
                    kwai_campaigns = KwaiCampaign.objects.filter(kwai=kwai)
                    for kwai_campaign in kwai_campaigns:
                        campaign = kwai_campaign.campaign
                        campaign.in_use = False
                        campaign.save()

                    kwai.delete()
                else:
                    invalid_uids.append(uid)

        if invalid_uids:
            return Response(
                {"error": "Alguns UIDs são inválidos ou não encontrados.",
                 "invalid_uids": invalid_uids},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"detail": "Contas Kwai excluídas com sucesso."},
            status=status.HTTP_200_OK
        )


class CampaignsNotInUseView(APIView):
    """
    Endpoint para listar todas as campanhas que não estão em uso.
    """
    permission_classes = [permissions.IsAuthenticated]

    @campaigns_not_in_use_view_get_schema
    def get(self, request):
        try:
            campaigns = Campaign.objects.filter(in_use=False)

            valid_campaigns = []
            for campaign in campaigns:
                try:
                    uuid.UUID(str(campaign.uid))
                    valid_campaigns.append(campaign)
                except ValueError:
                    pass

            serializer = CampaignSerializer(
                valid_campaigns, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Erro ao listar campanhas não utilizadas."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Dashboard_campaigns(APIView):
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
