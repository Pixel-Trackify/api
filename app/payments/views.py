from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from plans.models import Plan
from .models import SubscriptionPayment, UserSubscription
from .serializers import PaymentSerializer
from django.utils.timezone import now, timedelta
from drf_spectacular.utils import extend_schema
from .gateways import get_gateway
from .schemas import payment_status_schema, payment_create_schema, payment_webhook_schema, payment_change_plan_schema


class PaymentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**payment_status_schema)
    def get(self, request, uid):
        payment = get_object_or_404(SubscriptionPayment, uid=uid)
        return Response({"status": payment.status}, status=status.HTTP_200_OK)


class PaymentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**payment_create_schema)
    def post(self, request):
        serializer = PaymentSerializer(
            data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        user = request.user

        try:
            plan = Plan.objects.get(uid=data['plan_uid'])
        except Plan.DoesNotExist:
            return Response({"error": "Plano não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Checagem de idempotência
        idempotency_key = f"{user.pk}-{plan.uid}-{data['paymentMethod']}"
        one_hour_ago = now() - timedelta(minutes=60)
        existing_payment = SubscriptionPayment.objects.filter(
            idempotency=idempotency_key,
            created_at__gte=one_hour_ago
        ).order_by('-created_at').first()
        if existing_payment and existing_payment.subscription.plan == plan:
            return Response({
                "message": "Pagamento já processado recentemente.",
                "payment": {
                    "uid": existing_payment.uid,
                    "status": existing_payment.status,
                    "price": existing_payment.price,
                    "payment_method": existing_payment.payment_method,
                    "gateway": existing_payment.gateway,
                    "gateway_response": existing_payment.gateway_response
                }
            }, status=status.HTTP_200_OK)
        
        # Criação do pagamento
        try:
            gateway_name = data['gateway']
            gateway = get_gateway(gateway_name)
            payment = gateway.generate_payment(
                user, plan, data['paymentMethod'])
            payment.gateway = gateway_name
            payment.save()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "message": "Pagamento criado com sucesso.",
            "payment": {
                "uid": payment.uid,
                "status": payment.status,
                "price": payment.price,
                "payment_method": payment.payment_method,
                "gateway": payment.gateway,
                "gateway_response": payment.gateway_response
            }
        }, status=status.HTTP_201_CREATED)


class PaymentChangePlanView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**payment_change_plan_schema)
    def put(self, request, uid):
        serializer = PaymentSerializer(
            data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        user = request.user

        try:
            plan = Plan.objects.get(uid=data['plan_uid'])
        except Plan.DoesNotExist:
            return Response({"error": "Plano não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        
        try:
            gateway_name = data['gateway']  
            gateway = get_gateway(gateway_name)
            payment = gateway.generate_payment(
                user, plan, data['paymentMethod'])
            payment.gateway = gateway_name
            payment.save()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "message": "Solicitação de troca de plano criada com sucesso.",
            "payment": {
                "uid": payment.uid,
                "status": payment.status,
                "price": payment.price,
                "payment_method": payment.payment_method,
                "gateway": payment.gateway,
                "gateway_response": payment.gateway_response
            }
        }, status=status.HTTP_201_CREATED)


class PaymentWebhookView(APIView):
    """
    Endpoint para processar notificações do gateway de pagamento.
    """
    @extend_schema(**payment_webhook_schema)
    def post(self, request):
        data = request.data

        # Valida os dados recebidos
        payment_id = data.get("paymentId")
        payment_status = data.get("status")

        if not payment_id or not payment_status:
            return Response({"error": "Dados inválidos."}, status=status.HTTP_400_BAD_REQUEST)

        # Busca o pagamento no banco de dados
        try:
            payment = SubscriptionPayment.objects.get(token=payment_id)
        except SubscriptionPayment.DoesNotExist:
            return Response({"error": "Pagamento não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Use o gateway correto salvo no pagamento
        gateway_name = payment.gateway
        gateway = get_gateway(gateway_name)
        gateway.update_payment_status(payment.uid, payment_status)

        return Response({"message": "Estado do pagamento atualizado com sucesso."}, status=status.HTTP_200_OK)
