from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from django.db import transaction
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import Integration, IntegrationRequest
from campaigns.models import Campaign
from .serializers import IntegrationSerializer, IntegrationRequestSerializer
from django.conf import settings
import logging
from .schema import schemas

logger = logging.getLogger('django')


@schemas['integration_view_set']
class IntegrationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar integrações.
    """
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uid'
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['created_at']
    search_fields = ['name', 'created_at', 'gateway']

    def get_queryset(self):
        """
        Retorna as integrações do usuário autenticado.
        """
        queryset = self.queryset.filter(user=self.request.user)

        return queryset

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

    def get_object(self):
        """
        Sobrescreve o método para buscar a integração pelo campo `uid` em vez de `id`.
        """
        obj = get_object_or_404(self.get_queryset(),
                                uid=self.kwargs.get(self.lookup_field))

        return obj

    def perform_create(self, serializer):
        """
        Salva a nova integração com o usuário autenticado e retorna a URL do webhook.
        """
        integration = serializer.save(user=self.request.user)
        webhook_url = self.build_webhook_url(integration)

        return Response(
            {
                "message": "Integração criada com sucesso.",
                "webhook_url": webhook_url,
                "integration": IntegrationSerializer(integration).data,
            },
            status=status.HTTP_201_CREATED,
        )

    def build_webhook_url(self, integration):
        """
        Constrói a URL do webhook com base no domínio configurado no .env.
        """
        base_url = settings.WEBHOOK_BASE_URL  # Obtém o domínio do .env
        return f"{base_url}{integration.gateway.lower()}/{integration.uid}/"

    def perform_update(self, serializer):
        """
        Atualiza a integração se o usuário autenticado for o proprietário.
        """
        instance = self.get_object()
        if instance.user != self.request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """
        Permite deletar uma única integração pela `uid` na URL.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Integração excluída com sucesso."},
            status=status.HTTP_200_OK
        )

    def perform_destroy(self, instance):
        """
        Deleta a integração pelo UUID se o usuário autenticado for o proprietário.
        """
        if instance.user != self.request.user:
            raise PermissionDenied(
                "Você não tem permissão para deletar esta integração.")
        instance.delete()

    @action(detail=False, methods=['post'], url_path='delete-multiple')
    def delete_multiple(self, request):
        """
        Permite deletar várias integrações enviando os UUIDs no corpo da requisição.
        """
        uids = request.data.get('uids', None)
        if not uids:
            return Response(
                {"error": "Nenhum UUID fornecido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Busca as integrações correspondentes ao usuário autenticado
        instances = self.get_queryset().filter(uid__in=uids)
        not_found_uids = set(
            uids) - set(instances.values_list('uid', flat=True))

        if not instances.exists():
            return Response(
                {"error": "Nenhuma integração encontrada para os UUIDs fornecidos."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Usa uma transação para garantir consistência
        with transaction.atomic():
            deleted_count = instances.delete()[0]

        # Retorna uma resposta detalhada
        return Response(
            {
                "message": f"{deleted_count} integração(ões) excluída(s) com sucesso.",
                # Lista de UUIDs não encontrados
                "not_found": list(not_found_uids)
            },
            status=status.HTTP_200_OK
        )


@schemas['integration_detail_view']
class IntegrationDetailView(APIView):
    """
    APIView para gerenciar uma integração específica.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, uid):
        """
        Retorna os detalhes de uma integração específica do usuário autenticado.
        """
        integration = get_object_or_404(
            Integration, uid=uid, user=request.user)
        serializer = IntegrationSerializer(integration)
        return Response(serializer.data)


@schemas['integrationrequest_detail_view']
class IntegrationRequestDetailView(APIView):
    """
    APIView para obter os detalhes de uma requisição de integração específica.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, transaction_id):
        """
        Retorna os detalhes de uma requisição de integração específica.
        """
        integration_request = get_object_or_404(
            IntegrationRequest, payment_id=transaction_id, integration__user=request.user)
        serializer = IntegrationRequestSerializer(integration_request)
        return Response(serializer.data)


@schemas['integrationrequest_list_view']
class IntegrationRequestListView(APIView):
    """
    APIView para listar todas as requisições de integração.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retorna uma lista de todas as requisições de integração do usuário autenticado.
        """
        integration_requests = IntegrationRequest.objects.filter(
            integration__user=request.user)
        serializer = IntegrationRequestSerializer(
            integration_requests, many=True)
        return Response(serializer.data)


class AvailableGatewaysView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, campaign_id=None):
        if campaign_id:
            # Inclui o gateway da campanha atual na listagem
            try:
                campaign = Campaign.objects.get(id=campaign_id)
                gateways = Integration.objects.filter(
                    Q(in_use=False) | Q(id=campaign.integration.id)
                )
                response = [{"id": g.id, "name": g.name,
                             "gateway": g.gateway} for g in gateways]
            except Campaign.DoesNotExist:
                return Response({"error": "Campaign not found."}, status=404)
        else:
            # Lista todas as opções do campo 'gateway'
            response = [{"id": key, "name": value}
                        for key, value in Integration._meta.get_field('gateway').choices]

        return Response(response)
