from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Campaign, CampaignView
from integrations.models import Integration
from .serializers import CampaignSerializer, CampaignViewSerializer
from user_agents import parse
import datetime
import logging
from .schema import schemas

logger = logging.getLogger(__name__)


@schemas['campaign_view_set']
class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uid'

    def get_queryset(self):
        """Retorna as campanhas do usuário autenticado"""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Vincula automaticamente o usuário logado à campanha"""
        logger.debug(
            f"Dados recebidos no serializer: {serializer.validated_data}")
        serializer.save(user=self.request.user)

        # Salva a campanha vinculada ao usuário e à integração
        logger.debug(
            f"Dados recebidos no serializer: {serializer.validated_data}")
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        """Deleta a campanha se o usuário autenticado for o proprietário"""
        if instance.user != self.request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        instance.delete()


@schemas['kwai_webhook_view']
class KwaiWebhookView(APIView):
    permission_classes = [AllowAny]  # Permitir acesso público

    def get(self, request, uid):
        action = request.query_params.get('action')
        campaign = get_object_or_404(Campaign, uid=uid)

        # Capturar User-Agent e IP
        user_agent_string = request.META.get('HTTP_USER_AGENT', 'unknown')
        user_agent = parse(user_agent_string)
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
            price_unit = campaign.CPM / 1000
            campaign.total_ads += price_unit

            if action == 'view':
                campaign.total_views += 1
            elif action == 'click':
                campaign.total_clicks += 1

            campaign.save()

            logger.debug(
                f"Campaign {campaign.id} updated: Total Ads: {campaign.total_ads}, Total Views: {campaign.total_views}, Total Clicks: {campaign.total_clicks}")

            return Response({"status": "success", "message": "Campaign updated successfully."})
        else:
            logger.error(f"Error saving CampaignView: {serializer.errors}")
            return Response(serializer.errors, status=400)