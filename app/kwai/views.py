from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from campaigns.models import Campaign
from datetime import datetime, timedelta
from .services import get_financial_data
from .models import KwaiCampaign
from .serializers import KwaiSerializer, CampaignSerializer
from .models import Kwai, KwaiCampaign
from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.utils.html import strip_tags
import html
import re
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
    serializer_class = KwaiSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    lookup_field = 'uid'
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_queryset(self):
        return Kwai.objects.filter(user=self.request.user, deleted=False)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        search_param = self.request.query_params.get('search', None)

        if search_param:
            try:
                search_param.encode('latin-1')
            except UnicodeEncodeError:
                raise ValidationError(
                    {"search": "O parâmetro de busca contém caracteres inválidos."})

            if html.unescape(strip_tags(search_param)) != search_param:
                raise ValidationError(
                    {"search": "O parâmetro de busca contém caracteres inválidos."})

        return queryset

    @kwai_list_view_get_schema
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            if not queryset.exists():
                return Response(
                    {"count": 0, "detail": "Nenhuma campanha encontrada com os critérios de busca.", "results": []}
                )
        except Exception as e:
            return Response(
                {"count": 0, "results": [],
                    "detail": "O parâmetro de busca contém caracteres inválidos."},
            )

        return super().list(request, *args, **kwargs)

    @kwai_create_view_post_schema
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @kwai_get_view_schema
    def retrieve(self, request, uid=None, *args, **kwargs):
        try:
            uuid.UUID(uid)
        except (ValueError, TypeError):
            return Response({"error": "UID inválido."}, status=status.HTTP_400_BAD_REQUEST)

        kwai = self.get_queryset().filter(uid=uid, user=request.user, deleted=False).first()
        if not kwai:
            return Response({"error": "Conta Kwai não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(kwai)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @kwai_put_view_schema
    def update(self, request, uid=None, *args, **kwargs):
        try:
            uuid.UUID(uid)
        except (ValueError, TypeError):
            return Response({"error": "UID inválido."}, status=status.HTTP_400_BAD_REQUEST)

        kwai = self.get_queryset().filter(uid=uid, user=request.user, deleted=False).first()
        if not kwai:
            return Response({"error": "Conta Kwai não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        if not request.data:
            return Response({
                "name": [
                    "Este campo é obrigatório."
                ],
                "campaigns": [
                    "Este campo é obrigatório."
                ]
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(kwai, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

            campaign_uids = [campaign.get('uid')
                             for campaign in campaigns_data]
            campaigns = Campaign.objects.filter(
                uid__in=campaign_uids, deleted=False)

            if len(campaigns) != len(campaign_uids):
                return Response(
                    {"error": "Algumas campanhas fornecidas não foram encontradas."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        with transaction.atomic():
            current_campaigns = set(Campaign.objects.filter(
                kwai_campaigns__kwai=kwai, deleted=False))
            new_campaigns = set(campaigns)

            removed_campaigns = current_campaigns - new_campaigns

            for campaign in removed_campaigns:
                campaign.in_use = False
                campaign.save()

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
        try:
            uuid.UUID(uid)
        except (ValueError, TypeError):
            return Response({"error": "UID inválido."}, status=status.HTTP_400_BAD_REQUEST)

        kwai = self.get_queryset().filter(uid=uid, deleted=False).first()
        if not kwai:
            return Response({"error": "Conta Kwai não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        # Verifica se o usuário autenticado é o proprietário da conta Kwai
        if kwai.user != request.user:
            return Response(
                {"error": "Você não tem permissão para excluir esta conta Kwai."},
                status=status.HTTP_403_FORBIDDEN
            )

        with transaction.atomic():
            kwai_campaigns = KwaiCampaign.objects.filter(kwai=kwai)
            for kwai_campaign in kwai_campaigns:
                campaign = kwai_campaign.campaign
                campaign.in_use = False
                campaign.save()

            kwai_campaigns.delete()
            kwai.deleted = True
            kwai.save()

        return Response({"message": "Conta Kwai excluída com sucesso."}, status=status.HTTP_200_OK)

    @kwai_multiple_delete_schema
    @action(detail=False, methods=['post'], url_path='delete-multiple')
    def delete_multiple(self, request):
        if not request.user:
            return Response(
                {"error": "Nenhum Usuário encontrado."},
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

                kwai = Kwai.objects.filter(
                    uid=uid, user=request.user, deleted=False).first()
                if kwai:
                    kwai_campaigns = KwaiCampaign.objects.filter(kwai=kwai)
                    for kwai_campaign in kwai_campaigns:
                        campaign = kwai_campaign.campaign
                        campaign.in_use = False
                        campaign.save()
                    kwai.deleted = True
                    kwai.save()
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
            campaigns = Campaign.objects.filter(
                in_use=False, deleted=False).order_by('-created_at')

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

        start_date = request.query_params.get('start', None)
        end_date = request.query_params.get('end', None)

        try:

            if not start_date and not end_date:
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=30)

            elif start_date and not end_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                # Inclui o dia inteiro no filtro
                end_date = start_date + timedelta(days=1)

            elif start_date and end_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        except ValueError:

            raise ValidationError(
                {"detail": "Os parâmetros de data devem estar no formato YYYY-MM-DD."})

        # Obtém os dados financeiros filtrados pelo intervalo de datas
        data = get_financial_data(
            user=request.user, start_date=start_date, end_date=end_date)
        return Response(data, status=status.HTTP_200_OK)
