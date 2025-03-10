from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Integration, Transaction
from campaigns.models import Campaign
from django.db.models import Sum
from .serializers import TransactionSerializer, IntegrationSerializer, IntegrationRequestSerializer
from .zeroone_webhook import process_zeroone_webhook
import logging

logger = logging.getLogger(__name__)


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


class TransactionDetailView(APIView):
    """
    APIView para obter os detalhes de uma transação específica.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, transaction_id):
        """
        Retorna os detalhes de uma transação específica.
        """
        transaction = get_object_or_404(
            Transaction, transaction_id=transaction_id, integration__user=request.user)
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data)


class TransactionListView(APIView):
    """
    APIView para listar todas as transações.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retorna uma lista de todas as transações do usuário autenticado.
        """
        transactions = Transaction.objects.filter(
            integration__user=request.user)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
