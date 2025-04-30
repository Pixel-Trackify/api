from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from campaigns.models import Campaign
from .services import get_financial_data
from .models import KwaiCampaign
from .serializers import KwaiSerializer, CampaignSerializer
from .models import Kwai, KwaiCampaign
from django.db import transaction
import logging
import uuid
from .schema import (
    kwai_list_view_get_schema,
    kwai_create_view_post_schema,
    kwai_get_view_schema,
    kwai_put_view_schema,
    kwai_delete_view_schema,
    kwai_multiple_delete_schema,
    campaigns_not_in_use_view_get_schema, dashboard_campaigns_get_schema


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
    lookup_field = 'uid'
    http_method_names = ['get', 'post', 'put', 'delete']

    @kwai_list_view_get_schema
    def list(self, request, *args, **kwargs):
        """
        Lista todas as contas Kwai.
        """
        return super().list(request, *args, **kwargs)

    @kwai_create_view_post_schema
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

    @kwai_get_view_schema
    def retrieve(self, request, uid=None, *args, **kwargs):
        """
        Retorna os detalhes de uma conta Kwai específica.
        """
        try:
            uuid.UUID(uid)  
        except (ValueError, TypeError):
            return Response({"error": "UID inválido."}, status=status.HTTP_400_BAD_REQUEST)

        kwai = self.get_queryset().filter(uid=uid).first()
        if not kwai:
            return Response({"error": "Conta Kwai não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(kwai)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @kwai_put_view_schema
    def update(self, request, uid=None, *args, **kwargs):
        """
        Atualiza os dados de uma conta Kwai específica, incluindo campanhas associadas.
        """
        try:
            uuid.UUID(uid)  
        except (ValueError, TypeError):
            return Response({"error": "UID inválido."}, status=status.HTTP_400_BAD_REQUEST)

        kwai = self.get_queryset().filter(uid=uid).first()
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
                KwaiCampaign.objects.filter(kwai=kwai).delete()
                for campaign in campaigns:
                    campaign.in_use = True
                    campaign.save()
                    KwaiCampaign.objects.create(kwai=kwai, campaign=campaign)

        kwai.save()

        serializer = self.get_serializer(kwai)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @kwai_delete_view_schema
    def destroy(self, request, uid=None, *args, **kwargs):
        """
        Exclui uma conta Kwai específica.
        """
        try:
            uuid.UUID(uid)  # Valida se o 'uid' é um UUID válido
        except (ValueError, TypeError):
            return Response({"error": "UID inválido."}, status=status.HTTP_400_BAD_REQUEST)

        kwai = self.get_queryset().filter(uid=uid).first()
        if not kwai:
            return Response({"error": "Conta Kwai não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            KwaiCampaign.objects.filter(kwai=kwai).delete()
            kwai.delete()

        return Response({"message": "Conta Kwai excluída com sucesso."}, status=status.HTTP_200_OK)

    @kwai_multiple_delete_schema
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


@dashboard_campaigns_get_schema
class Dashboard_campaigns(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        data = get_financial_data(user=request.user)
        return Response(data, status=status.HTTP_200_OK)
