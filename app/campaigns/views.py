from rest_framework import viewsets, status, filters
from django.utils.timezone import now
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Campaign, FinanceLogs
from integrations.models import Integration
from .serializers import CampaignSerializer, CampaignViewSerializer
from user_agents import parse
from integrations.campaign_utils import recalculate_campaigns
from .finance_log_utils import update_finance_logs
from django.conf import settings
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

        # Usar o domínio configurado no .env
        base_webhook_url = settings.WEBHOOK_BASE_URL

        # Construir as URLs do webhook
        view_webhook_url = f"{base_webhook_url}{campaign.uid}/?action=view"
        click_webhook_url = f"{base_webhook_url}{campaign.uid}/?action=click"

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
            # Atualiza o campo `in_use` das integrações associadas às campanhas
            for campaign in instances:
                for integration in campaign.integrations.all():
                    integration.in_use = False
                    integration.save()
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
