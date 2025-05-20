from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework import serializers
import re
from django.utils.html import strip_tags
import html
from datetime import datetime, timedelta
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError, NotFound
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from .models import Campaign
from .serializers import CampaignSerializer
from django.conf import settings
import logging
from .schema import schemas


from django.urls import reverse

logger = logging.getLogger('django')


@schemas['campaign_view_set']
class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.filter(deleted=False)
    serializer_class = CampaignSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uid'
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['title', 'created_at']
    search_fields = ['title', 'description', 'method', 'created_at']

    def filter_queryset(self, queryset):
        """
        Sobrescreve o método filter_queryset para validar os parâmetros de busca.
        """
        queryset = super().filter_queryset(queryset)

        # Validação do parâmetro de busca
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

        # Filtros de intervalo de datas
        start_date = self.request.query_params.get('start', None)
        end_date = self.request.query_params.get('end', None)

        try:

            if not start_date and not end_date:
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=30)

            elif start_date and not end_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = start_date

            elif start_date and end_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

            queryset = queryset.filter(
                created_at__date__gte=start_date, created_at__date__lte=end_date)

        except ValueError:

            raise ValidationError(
                {"detail": "Os parâmetros de data devem estar no formato YYYY-MM-DD."})

        return queryset

    def get_queryset(self):
        """Retorna as campanhas do usuário autenticado"""
        return self.queryset.filter(user=self.request.user).prefetch_related('integrations')

    def list(self, request, *args, **kwargs):
        """
        Sobrescreve o método list para adicionar uma mensagem de erro
        caso nenhum dado seja encontrado na busca.
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            # Verifica se o queryset está vazio
            if not queryset.exists():
                return Response(
                    {"count": 0, "detail": "Nenhuma campanha encontrada com os critérios de busca.", "results": []}
                )
        except Exception as e:
            return Response(
                {"count": 0, "results": [],
                    "detail": "O parâmetro de busca contém caracteres inválidos."},
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

    def retrieve(self, request, *args, **kwargs):
        """Adiciona os links do webhook na resposta do detalhe da campanha"""
        response = super().retrieve(request, *args, **kwargs)

        # Recuperar a campanha detalhada
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
        Se o UID não existir, retorna mensagem personalizada.
        """
        uid = kwargs.get('uid')
        try:
            instance = self.get_queryset().get(uid=uid)
        except Campaign.DoesNotExist:
            return Response(
                {"detail": 'Nenhuma campanha corresponde à consulta fornecida.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if getattr(instance, "in_use", False):
            return Response(
                {"error": "Não é possível excluir uma campanha que está em uso."},
                status=status.HTTP_400_BAD_REQUEST
            )

        instance.delete()
        return Response(
            {"message": "Campanha excluída com sucesso."},
            status=status.HTTP_200_OK
        )

    def perform_destroy(self, instance):
        """
        Deleta a campanha pelo UUID se o usuário autenticado for o proprietário.
        """
        if instance.user != self.request.user:
            raise PermissionDenied("Não foi possível deletar esta campanha.")
        if getattr(instance, "in_use", False):
            raise ValidationError(
                "Não é possível excluir uma campanha que está em uso.")
        instance.deleted = True
        instance.save()

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

        instances = self.get_queryset().filter(uid__in=uids)
        not_found_uids = set(
            uids) - set(instances.values_list('uid', flat=True))

        if not instances.exists():
            return Response(
                {"error": "Nenhuma campanha encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )

        in_use = []
        for campaign in instances:
            if getattr(campaign, "in_use", False):
                in_use.append(str(campaign.uid))
        if in_use:
            return Response(
                {
                    "error": "Não é possível excluir campanhas em uso.",
                    "in_use": in_use
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            for campaign in instances:
                for integration in campaign.integrations.all():
                    integration.in_use = False
                    integration.save()
            deleted_count = instances.count()
            instances.update(deleted=True)

        return Response(
            {
                "message": f"{deleted_count} campanha(s) excluída(s) com sucesso.",
                "not_found": list(not_found_uids)
            },
            status=status.HTTP_200_OK
        )
