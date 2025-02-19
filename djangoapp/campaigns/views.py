from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from .models import Campaign, CampaignView
from .serializers import CampaignSerializer, CampaignViewSerializer
from user_agents import parse
import datetime


class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [IsAuthenticated]


class KwaiWebhookView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        action = request.query_params.get('action')
        campaign = get_object_or_404(Campaign, id=id)

        # Capturar User-Agent e IP
        user_agent_string = request.META.get('HTTP_USER_AGENT', 'unknown')
        user_agent = parse(user_agent_string)
        ip_address = request.META.get(
            'HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))

        # Gerar timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Criar o dicionário 
        server_data = {
            "timestamp": timestamp,
            "server": {
                "HTTP_USER_AGENT": user_agent_string,
                "HTTP_X_FORWARDED_FOR": ip_address,
                "HTTP_X_REAL_IP": request.META.get("HTTP_X_REAL_IP", ip_address),
                "HTTP_X_REAL_PORT": request.META.get("HTTP_X_REAL_PORT", ""),
                "HTTP_X_FORWARDED_PORT": request.META.get("HTTP_X_FORWARDED_PORT", ""),
                "HTTP_X_PORT": request.META.get("HTTP_X_PORT", ""),
                "HTTP_X_LSCACHE": request.META.get("HTTP_X_LSCACHE", ""),
                "HTTP_X_CLIENT_INFO": f"model={user_agent.device.family};os={user_agent.os.family};network=WIFI;",
                "REMOTE_ADDR": ip_address,
                "SERVER_ADDR": request.META.get("SERVER_ADDR", ""),
                "SERVER_NAME": request.META.get("SERVER_NAME", ""),
                "SERVER_PORT": request.META.get("SERVER_PORT", ""),
                "REQUEST_SCHEME": request.META.get("REQUEST_SCHEME", "https"),
                "REQUEST_URI": request.get_full_path(),
                "QUERY_STRING": request.META.get("QUERY_STRING", ""),
                "SCRIPT_URI": request.build_absolute_uri(),
                "REQUEST_METHOD": request.method,
                "SERVER_PROTOCOL": request.META.get("SERVER_PROTOCOL", ""),
                "SERVER_SOFTWARE": request.META.get("SERVER_SOFTWARE", ""),
                "REQUEST_TIME_FLOAT": request.META.get("REQUEST_TIME_FLOAT", ""),
                "REQUEST_TIME": request.META.get("REQUEST_TIME", ""),
            }
        }

        # Criar uma entrada no CampaignView
        data = {
            'campaign': campaign.id,
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

            return Response({"status": "success", "message": "Campaign updated successfully.", "server_data": server_data})
        else:
            return Response(serializer.errors, status=400)
