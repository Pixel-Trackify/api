from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from django.urls import reverse
from django.db import transaction
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import Integration, IntegrationRequest
from .serializers import IntegrationSerializer, IntegrationRequestSerializer
from .zeroone_webhook import process_zeroone_webhook
from .disrupty_webhook import process_disrupty_webhook
from .vega_checkout_webhook import process_vega_checkout_webhook
from .cloudfy_webhook import process_cloudfy_webhook
from .tribopay_webhook import process_tribopay_webhook
from .wolfpay_webhook import process_wolfpay_webhook
from .westpay_webhook import process_westpay_webhook
from .sunize_webhook import process_sunize_webhook
import logging
from .schema import schemas

logger = logging.getLogger(__name__)


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
                {"detail": "Nenhuma campanha encontrada com os critérios de busca."},
                status=status.HTTP_404_NOT_FOUND
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
        Constrói a URL do webhook com base no gateway e no UID da integração.
        """
        return self.request.build_absolute_uri(
            reverse(
                f"{integration.gateway.lower()}-webhook",
                kwargs={"uid": integration.uid},
            )
        )

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
    """
    Endpoint para listar os gateways disponíveis para integração.
    """
    permission_classes = [AllowAny]  # Permitir acesso público

    def get(self, request):
        gateways = [{"id": key, "name": value}
                    for key, value in Integration._meta.get_field('gateway').choices]
        return Response(gateways)


class BaseWebhookView(APIView):
    """
    Classe base para processar notificações de webhooks de gateways de pagamento.
    """
    permission_classes = [AllowAny]

    @property
    def gateway_name(self):
        """
        Propriedade que deve ser sobrescrita pelas subclasses para definir o nome do gateway.
        """
        raise NotImplementedError("Subclasses must define 'gateway_name'.")

    @property
    def process_function(self):
        """
        Propriedade que deve ser sobrescrita pelas subclasses para definir a função de processamento.
        """
        raise NotImplementedError("Subclasses must define 'process_function'.")

    def post(self, request, uid):
        """
        Processa notificações de webhooks.
        """
        # Recupera a integração ativa
        integration = get_object_or_404(
            Integration, uid=uid, deleted=False, status='active'
        )

        # Valida se o gateway da integração corresponde ao gateway esperado (case insensitive)
        if integration.gateway.lower() != self.gateway_name.lower():
            return Response(
                {"error": f"Invalid gateway for this integration. Expected: {self.gateway_name}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Processa o webhook
        try:
            self.process_function(request.data, integration)
            return Response({"message": "Webhook processed successfully"}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error processing webhook: {e}", exc_info=True)
            return Response({"error": "Error processing webhook"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@schemas['zeroone_webhook_view']
class ZeroOneWebhookView(BaseWebhookView):
    @property
    def gateway_name(self):
        return 'ZeroOne'

    @property
    def process_function(self):
        return process_zeroone_webhook


@schemas['ghostspay_webhook_view']
class GhostsPayWebhookView(BaseWebhookView):
    @property
    def gateway_name(self):
        return 'GhostsPay'

    @property
    def process_function(self):
        return process_zeroone_webhook


@schemas['paradisepag_webhook_view']
class ParadisePagWebhookView(BaseWebhookView):
    @property
    def gateway_name(self):
        return 'ParadisePag'

    @property
    def process_function(self):
        return process_zeroone_webhook


@schemas['disrupty_webhook_view']
class DisruptyWebhookView(BaseWebhookView):
    @property
    def gateway_name(self):
        return 'Disrupty'

    @property
    def process_function(self):
        return process_disrupty_webhook


@schemas['wolfpay_webhook_view']
class WolfPayWebhookView(BaseWebhookView):
    @property
    def gateway_name(self):
        return 'WolfPay'

    @property
    def process_function(self):
        return process_wolfpay_webhook


@schemas['vegacheckout_webhook_view']
class VegaCheckoutWebhookView(BaseWebhookView):
    @property
    def gateway_name(self):
        return 'VegaCheckout'

    @property
    def process_function(self):
        return process_vega_checkout_webhook


@schemas['cloudfy_webhook_view']
class CloudFyWebhookView(BaseWebhookView):
    @property
    def gateway_name(self):
        return 'CloudFy'

    @property
    def process_function(self):
        return process_cloudfy_webhook


@schemas['tribopay_webhook_view']
class TriboPayWebhookView(BaseWebhookView):
    @property
    def gateway_name(self):
        return 'TriboPay'

    @property
    def process_function(self):
        return process_tribopay_webhook


@schemas['westpay_webhook_view']
class WestPayWebhookView(BaseWebhookView):
    @property
    def gateway_name(self):
        return 'WestPay'

    @property
    def process_function(self):
        return process_westpay_webhook


@schemas['sunize_webhook_view']
class SunizeWebhookView(BaseWebhookView):
    @property
    def gateway_name(self):
        return 'Sunize'

    @property
    def process_function(self):
        return process_sunize_webhook
