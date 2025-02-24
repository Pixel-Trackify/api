from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Integration, Transaction
from campaigns.models import Campaign
from django.db.models import Sum
from .serializers import TransactionSerializer, IntegrationSerializer


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
    APIView para processar webhooks do gateway de pagamento ZeroOne.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, uid):
        """
        Processa uma requisição POST recebida do webhook.
        """
        # Obtém a integração correspondente ao UID fornecido
        integration = get_object_or_404(Integration, uid=uid)

        # Extrai os dados da transação do corpo da requisição
        transaction_id = request.data.get('id')
        transaction_status = request.data.get('status')
        amount = request.data.get('amount')

        # Verifica se todos os campos obrigatórios estão presentes
        if not transaction_id or not transaction_status or not amount:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Cria ou atualiza a transação com os dados fornecidos
            transaction, created = Transaction.objects.update_or_create(
                transaction_id=transaction_id,
                defaults={
                    'integration': integration,
                    'status': transaction_status,
                    'amount': amount
                }
            )
        except Exception as e:
            return Response({"error": "Error processing transaction"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Recalcula as informações na tabela Campaign
        try:
            self.recalculate_campaigns(integration)
        except Exception as e:
            return Response({"error": "Error recalculating campaigns"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Transaction processed successfully"}, status=status.HTTP_200_OK)

    def recalculate_campaigns(self, integration):
        """
        Recalcula as informações das campanhas associadas à integração.
        """
        campaigns = Campaign.objects.filter(integrations=integration)
        for campaign in campaigns:
            transactions = Transaction.objects.filter(integration=integration)
            total_approved = transactions.filter(status='APPROVED').count()
            total_pending = transactions.filter(status='PENDING').count()
            amount_approved = transactions.filter(
                status='APPROVED').aggregate(Sum('amount'))['amount__sum'] or 0
            amount_pending = transactions.filter(status='PENDING').aggregate(
                Sum('amount'))['amount__sum'] or 0
            profit = amount_approved - amount_pending
            roi = (profit / amount_approved) * \
                100 if amount_approved > 0 else 0

            campaign.total_approved = total_approved
            campaign.total_pending = total_pending
            campaign.amount_approved = amount_approved
            campaign.amount_pending = amount_pending
            campaign.profit = profit
            campaign.ROI = roi
            campaign.save()


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
            Transaction, transaction_id=transaction_id)
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data)


class TransactionListView(APIView):
    """
    APIView para listar todas as transações.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = Transaction.objects.all()
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
