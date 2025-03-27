from rest_framework import viewsets, status, filters
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Campaign, CampaignView
from integrations.models import Integration
from .serializers import CampaignSerializer, CampaignViewSerializer
from user_agents import parse
from integrations.campaign_utils import recalculate_campaigns
import datetime
import logging
from .schema import schemas
from decimal import Decimal

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
        return self.queryset.filter(user=self.request.user)

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
        logger.debug(
            f"Dados recebidos no serializer: {serializer.validated_data}")
        serializer.save(user=self.request.user)

        # Salva a campanha vinculada ao usuário e à integração
        logger.debug(
            f"Dados recebidos no serializer: {serializer.validated_data}")
        serializer.save(user=self.request.user)

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

            # Atualiza o total_ads com base no CPM
            price_unit = Decimal(campaign.CPM) / 1000
            campaign.total_ads = Decimal(campaign.total_ads) + price_unit
            campaign.save()

            # Calcula os valores necessários para recalculate_campaigns
            total_ads = campaign.total_ads
            amount_approved = campaign.amount_approved

            # Recalcular profit e ROI para todas as integrações associadas
            for integration in campaign.integrations.all():
                recalculate_campaigns(campaign, total_ads, amount_approved)

            logger.debug(
                f"Campaign {campaign.id} updated: Total Ads: {campaign.total_ads}, Total Views: {campaign.total_views}, Total Clicks: {campaign.total_clicks}")

            return Response({"status": "success", "message": "Campaign updated successfully."})
        else:
            logger.error(f"Error saving CampaignView: {serializer.errors}")
            return Response(serializer.errors, status=400)
