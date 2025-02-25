from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from .models import Campaign, CampaignView
from .serializers import CampaignSerializer, CampaignViewSerializer
from user_agents import parse
import datetime
import logging

logger = logging.getLogger(__name__)

class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [IsAuthenticated]


class KwaiWebhookView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, uid):
        action = request.query_params.get('action')
        campaign = get_object_or_404(Campaign, uid=uid)

        # Capturar User-Agent e IP
        user_agent_string = request.META.get('HTTP_USER_AGENT', 'unknown')
        user_agent = parse(user_agent_string)
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))

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

            logger.debug(f"Campaign {campaign.id} updated: Total Ads: {campaign.total_ads}, Total Views: {campaign.total_views}, Total Clicks: {campaign.total_clicks}")

            return Response({"status": "success", "message": "Campaign updated successfully."})
        else:
            logger.error(f"Error saving CampaignView: {serializer.errors}")
            return Response(serializer.errors, status=400)