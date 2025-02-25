from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Subscription, SubscriptionPayment
from .serializers import SubscriptionSerializer, SubscriptionPaymentSerializer
from plans.models import Plan
from django.utils import timezone
from datetime import timedelta
from .utils import update_payment_status

class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_uid = request.data.get('plan_uid')
        payment_method = request.data.get('payment_method')
        idempotency = request.data.get('idempotency')
        token = request.data.get('token')
        cpf = request.data.get('cpf')

        if not plan_uid or not payment_method or not idempotency or not token:
            return Response({"error": "Parâmetros obrigatórios ausentes."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            plan = Plan.objects.get(uid=plan_uid)
        except Plan.DoesNotExist:
            return Response({"error": "Plano não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        subscription, created = Subscription.objects.get_or_create(user=request.user, plan=plan, defaults={'status': 'pending', 'expiration': timezone.now() + timedelta(days=30)})

        if not created and subscription.status == 'active':
            return Response({"error": "Usuário já possui uma assinatura ativa."}, status=status.HTTP_400_BAD_REQUEST)

        payment = SubscriptionPayment.objects.create(
            subscription=subscription,
            idempotency=idempotency,
            payment_method=payment_method,
            token=token,
            price=plan.price,
            status=0,
            user=request.user
        )

        # Simulação de resposta do gateway de pagamento
        gateway_response = {
            "uid": payment.uid,
            "payment_method": payment_method,
            "status": "pending"
        }

        if payment_method == 'pix':
            gateway_response["qr_code"] = "QRCodeSimulado"
            gateway_response["pix_key"] = "ChavePixSimulada"
        elif payment_method == 'boleto':
            gateway_response["boleto_url"] = "URLBoletoSimulada"
        elif payment_method in ['credit_card', 'debit_card']:
            gateway_response["status"] = "paid"

        payment.gateway_response = gateway_response
        payment.save()

        # Atualizar o estado do pagamento se for pago imediatamente
        if payment_method in ['credit_card', 'debit_card'] and gateway_response["status"] == "paid":
            update_payment_status(payment.uid, 'paid')

        return Response(gateway_response, status=status.HTTP_201_CREATED)

class PaymentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, uid):
        try:
            payment = SubscriptionPayment.objects.get(uid=uid, user=request.user)
        except SubscriptionPayment.DoesNotExist:
            return Response({"error": "Pagamento não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"status": payment.status}, status=status.HTTP_200_OK)

class PaymentWebhookView(APIView):
    def post(self, request, gateway_name):
        # Processar a notificação do gateway de pagamento
        payment_uid = request.data.get('payment_uid')
        status = request.data.get('status')

        result = update_payment_status(payment_uid, status)
        if "error" in result:
            return Response(result, status=status.HTTP_404_NOT_FOUND)

        return Response(result, status=status.HTTP_200_OK)