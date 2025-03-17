from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
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

    def get_queryset(self):
        """
        Retorna as integrações do usuário autenticado.
        """
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Salva a nova integração com o usuário autenticado.
        """
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """
        Atualiza a integração se o usuário autenticado for o proprietário.
        """
        instance = self.get_object()
        if instance.user != self.request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer.save()

    def perform_destroy(self, instance):
        """
        Deleta a integração se o usuário autenticado for o proprietário.
        """
        if instance.user != self.request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        instance.delete()


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

    def delete(self, request, uid):
        """
        Deleta uma integração específica do usuário autenticado.
        """
        integration = get_object_or_404(
            Integration, uid=uid, user=request.user)
        integration.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@schemas['zeroone_webhook_view']
class ZeroOneWebhookView(APIView):
    """
    APIView para processar notificações de transações do gateway de pagamento ZeroOne.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, uid):
        """
        Processa notificações de transações do gateway de pagamento ZeroOne.
        """
        integration = get_object_or_404(
            Integration, uid=uid, user=request.user, deleted=False, status='active')

        try:
            # Processa o webhook usando a função separada
            process_zeroone_webhook(request.data, integration)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error processing transaction: {e}")
            return Response({"error": "Error processing transaction"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Transaction processed successfully"}, status=status.HTTP_200_OK)


@schemas['ghostspay_webhook_view']
class GhostsPayWebhookView(APIView):
    """
    APIView para processar notificações de transações do gateway de pagamento GhostsPay.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, uid):
        """
        Processa notificações de transações do gateway de pagamento GhostsPay.
        """
        integration = get_object_or_404(
            Integration, uid=uid, user=request.user, deleted=False, status='active')

        try:
            # Processa o webhook usando a função separada
            process_zeroone_webhook(request.data, integration)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error processing transaction: {e}")
            return Response({"error": "Error processing transaction"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Transaction processed successfully"}, status=status.HTTP_200_OK)


@schemas['paradisepag_webhook_view']
class ParadisePagWebhookView(APIView):
    """
    APIView para processar notificações de transações do gateway de pagamento ParadisePag.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, uid):
        """
        Processa notificações de transações do gateway de pagamento ParadisePag.
        """
        integration = get_object_or_404(
            Integration, uid=uid, user=request.user, deleted=False, status='active')

        try:
            # Processa o webhook usando a função separada
            process_zeroone_webhook(request.data, integration)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error processing transaction: {e}")
            return Response({"error": "Error processing transaction"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Transaction processed successfully"}, status=status.HTTP_200_OK)


@schemas['disrupty_webhook_view']
class DisruptyWebhookView(APIView):
    """
    APIView para processar notificações de transações do gateway de pagamento Disrupty.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, uid):
        """
        Processa notificações de transações do gateway de pagamento Disrupty.
        """
        integration = get_object_or_404(
            Integration, uid=uid, user=request.user, deleted=False, status='active')

        try:
            # Processa o webhook usando a função separada
            process_disrupty_webhook(request.data, integration)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error processing transaction: {e}")
            return Response({"error": "Error processing transaction"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Transaction processed successfully"}, status=status.HTTP_200_OK)


@schemas['wolfpay_webhook_view']
class WolfPayWebhookView(APIView):
    """
    APIView para processar notificações de transações do gateway de pagamento WolfPay.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, uid):
        """
        Processa notificações de transações do gateway de pagamento WolfPay.
        """
        integration = get_object_or_404(
            Integration, uid=uid, user=request.user, deleted=False, status='active')

        try:
            # Processa o webhook usando a função separada
            process_wolfpay_webhook(request.data, integration)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error processing transaction: {e}")
            return Response({"error": "Error processing transaction"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Transaction processed successfully"}, status=status.HTTP_200_OK)


@schemas['vegacheckout_webhook_view']
class VegaCheckoutWebhookView(APIView):
    """
    APIView para processar notificações de transações do gateway de pagamento Vega Checkout.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, uid):
        """
        Processa notificações de transações do gateway de pagamento Vega Checkout.
        """
        integration = get_object_or_404(
            Integration, uid=uid, user=request.user, deleted=False, status='active')

        try:
            # Processa o webhook usando a função separada
            process_vega_checkout_webhook(request.data, integration)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error processing transaction: {e}")
            return Response({"error": "Error processing transaction"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Transaction processed successfully"}, status=status.HTTP_200_OK)


@schemas['cloudfy_webhook_view']
class CloudFyWebhookView(APIView):
    """
    APIView para processar notificações de transações do gateway de pagamento CloudFy.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, uid):
        """
        Processa notificações de transações do gateway de pagamento CloudFy.
        """
        integration = get_object_or_404(
            Integration, uid=uid, user=request.user, deleted=False, status='active')

        try:
            # Processa o webhook usando a função separada
            process_cloudfy_webhook(request.data, integration)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error processing transaction: {e}")
            return Response({"error": "Error processing transaction"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Transaction processed successfully"}, status=status.HTTP_200_OK)


@schemas['tribopay_webhook_view']
class TriboPayWebhookView(APIView):
    """
    APIView para processar notificações de transações do gateway de pagamento Tribo Pay.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, uid):
        """
        Processa notificações de transações do gateway de pagamento Tribo Pay.
        """
        integration = get_object_or_404(
            Integration, uid=uid, user=request.user, deleted=False, status='active')

        data = request.data
        required_fields = ['transaction',
                           'payment_status', 'payment_method', 'amount']

        # Verifica se todos os campos obrigatórios estão presentes
        for field in required_fields:
            if field not in data:
                return Response({"error": f"Missing required field: {field}"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            process_tribopay_webhook(data, integration)
            return Response({"message": "Webhook processado com sucesso."}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Erro ao processar o webhook do Tribo Pay: {e}")
            return Response({"error": "Erro ao processar o webhook"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@schemas['westpay_webhook_view']
class WestPayWebhookView(APIView):
    """
    APIView para processar notificações de transações do gateway de pagamento WestPay.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, uid):
        """
        Processa notificações de transações do gateway de pagamento WestPay.
        """
        integration = get_object_or_404(
            Integration, uid=uid, user=request.user, deleted=False, status='active')

        try:
            # Processa o webhook usando a função separada
            process_westpay_webhook(request.data, integration)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error processing transaction: {e}")
            return Response({"error": "Error processing transaction"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Transaction processed successfully"}, status=status.HTTP_200_OK)


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
