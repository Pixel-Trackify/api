from rest_framework import viewsets, status, filters
from django.utils.timezone import now
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Campaign, Expense
from integrations.models import Integration
from .serializers import CampaignSerializer, CampaignViewSerializer
from user_agents import parse
from integrations.campaign_utils import recalculate_campaigns
import datetime
import logging
from .schema import schemas
from decimal import Decimal
import os
from django.urls import reverse

logger = logging.getLogger('django')


@schemas['campaign_view_set']
class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uid'
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['title', 'created_at']
    search_fields = ['title', 'created_at']

    def get_queryset(self):
        """Retorna as campanhas do usuário autenticado"""
        return self.queryset.filter(user=self.request.user).prefetch_related('integrations')

    def list(self, request, *args, **kwargs):
        """
        Sobrescreve o método list para adicionar uma mensagem de erro
        caso nenhum dado seja encontrado na busca.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Verifica se o queryset está vazio
        if not queryset.exists():
            return Response(
                {"total": 0, "detail": "Nenhuma campanha encontrada com os critérios de busca.", "results": []}
            )

        # Caso contrário, retorna os resultados normalmente
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """Vincula automaticamente o usuário logado à campanha"""
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Sobrescreve o método create para incluir as URLs do webhook na resposta"""
        response = super().create(request, *args, **kwargs)

        # Recuperar a campanha criada
        campaign = Campaign.objects.get(uid=response.data['uid'])

        # Construir as URLs do webhook dinamicamente
        view_webhook_url = request.build_absolute_uri(
            reverse("kwai-webhook", kwargs={"uid": campaign.uid})
        ) + "?action=view"

        click_webhook_url = request.build_absolute_uri(
            reverse("kwai-webhook", kwargs={"uid": campaign.uid})
        ) + "?action=click"

        # Adicionar as URLs do webhook na resposta
        response.data['view_webhook_url'] = view_webhook_url
        response.data['click_webhook_url'] = click_webhook_url

        return response

    def destroy(self, request, *args, **kwargs):
        """
        Permite deletar uma única campanha pela `uid` na URL.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Campanha excluída com sucesso."},
            status=status.HTTP_200_OK
        )

    def perform_destroy(self, instance):
        """
        Deleta a campanha pelo UUID se o usuário autenticado for o proprietário.
        """
        if instance.user != self.request.user:
            raise PermissionDenied(
                "Você não tem permissão para deletar esta campanha."
            )
        instance.delete()

    @action(detail=False, methods=['post'], url_path='delete-multiple')
    def delete_multiple(self, request):
        """
        Permite deletar várias campanhas enviando os UUIDs no corpo da requisição.
        """
        uids = request.data.get('uids', None)
        if not uids:
            return Response(
                {"error": "Nenhum UUID fornecido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Busca as campanhas correspondentes ao usuário autenticado
        instances = self.get_queryset().filter(uid__in=uids)
        not_found_uids = set(
            uids) - set(instances.values_list('uid', flat=True))

        if not instances.exists():
            return Response(
                {"error": "Nenhuma campanha encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Usa uma transação para garantir consistência
        with transaction.atomic():
            deleted_count = instances.delete()[0]

        # Retorna uma resposta detalhada
        return Response(
            {
                "message": f"{deleted_count} campanha(s) excluída(s) com sucesso.",
                # Lista de UUIDs não encontrados
                "not_found": list(not_found_uids)
            },
            status=status.HTTP_200_OK
        )


@schemas['kwai_webhook_view']
class KwaiWebhookView(APIView):
    permission_classes = [AllowAny]  # Permitir acesso público
    authentication_classes = []

    def get(self, request, uid):
        action = request.query_params.get('action')
        campaign = get_object_or_404(Campaign, uid=uid)

        # Capturar User-Agent e IP
        user_agent_string = request.META.get('HTTP_USER_AGENT', 'unknown')
        ip_address = request.META.get(
            'HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))

        # Criar uma entrada no CampaignView
        data = {
            'campaign': campaign.uid,
            'user_agent': user_agent_string,
            'ip_address': ip_address,
            'action': action
        }
        serializer = CampaignViewSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            # Atualizar os campos da campanha
            if action == 'view':
                campaign.total_views += 1
            elif action == 'click':
                campaign.total_clicks += 1

            # Calcula o preço unitário com base no CPM
            price_unit = Decimal(campaign.CPM) / 1000

            # Verifica se já existe um registro para a campanha e a data atual
            today = now().date()
            expense_log, created = Expense.objects.get_or_create(
                campaign=campaign,
                date=today,
                defaults={'total_ads': Decimal('0.0'), 'views': 0, 'clicks': 0}
            )

            # Atualiza os valores na tabela expense_log
            expense_log.total_ads += price_unit
            if action == 'view':
                expense_log.views += 1
            elif action == 'click':
                expense_log.clicks += 1
            expense_log.save()

            # Atualiza o total_ads na tabela Campaign
            campaign.total_ads += price_unit
            campaign.save()

            # Recalcular profit e ROI da campanha
            recalculate_campaigns(
                campaign, campaign.total_ads, campaign.amount_approved)

            if bool(int(os.getenv('DEBUG', 0))):
                logger.debug(
                    f"Campaign {campaign.id} updated: Total Ads: {campaign.total_ads}, Total Views: {campaign.total_views}, Total Clicks: {campaign.total_clicks}"
                )

            return Response({"status": "success", "message": "Campaign updated successfully."})
        else:
            logger.error(f"Error saving CampaignView: {serializer.errors}")
            return Response(serializer.errors, status=400)
