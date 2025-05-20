from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from plans.models import Plan
from .models import SubscriptionPayment, UserSubscription
from .serializers import PaymentSerializer, SubscriptionPlanSerializer, PlanInfoSerializer, PaymentOpenedSerializer, PaymentHistoricSerializer
from django.utils.timezone import now, timedelta
from drf_spectacular.utils import extend_schema
from .gateways import get_gateway
from .schemas import payment_status_schema, payment_create_schema, payment_webhook_schema, payment_change_plan_schema, subscription_info_schema
import uuid
import hashlib


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
        base_idempotency_key = f"{user.pk}-{plan.uid}-{data['paymentMethod']}"
        one_hour_ago = now() - timedelta(minutes=60)
        existing_payment = SubscriptionPayment.objects.filter(
            idempotency=base_idempotency_key
        ).order_by('-created_at').first()

        if existing_payment and existing_payment.subscription.plan == plan:
            if existing_payment.status == "paid":
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
            elif existing_payment.created_at < one_hour_ago:
                # Expira o antigo e gera novo idempotency_key
                existing_payment.status = False
                existing_payment.save()
                if existing_payment.subscription:
                    existing_payment.subscription.status = "expired"
                    existing_payment.subscription.save()
                raw_key = f"{base_idempotency_key}-{uuid.uuid4()}"
                idempotency_key = hashlib.sha256(
                    raw_key.encode()).hexdigest()[:100]
            else:
                # Retorna o mesmo pagamento se ainda está dentro de 60 minutos
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
        else:
            idempotency_key = base_idempotency_key

        # Criação do pagamento
        try:
            gateway_name = data['gateway']
            gateway = get_gateway(gateway_name)
            payment = gateway.generate_payment(
                user, plan, data['paymentMethod'], idempotency_key=idempotency_key)
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


class SubscriptionInfoView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**subscription_info_schema)
    def get(self, request):
        user = request.user

        # Assinatura do usuário
        subscription = UserSubscription.objects.filter(
            user=user).select_related('plan').order_by('-expiration').first()
        plan_data = SubscriptionPlanSerializer(
            subscription).data if subscription else {}

        # Pagamentos em aberto
        payments_opened = SubscriptionPayment.objects.filter(
            subscription__user=user, status='False'
        ).order_by('-created_at')
        payments_opened_list = PaymentOpenedSerializer(
            payments_opened, many=True).data

        # Histórico de pagamentos pagos
        payments_historic = SubscriptionPayment.objects.filter(
            subscription__user=user, status='True'
        ).order_by('-created_at')
        payments_historic_list = PaymentHistoricSerializer(
            payments_historic, many=True).data

        # Planos disponíveis
        plans = Plan.objects.all()
        plans_list = PlanInfoSerializer(plans, many=True).data

        return Response({
            "plan": plan_data,
            "payments_opened": payments_opened_list,
            "payments_historic": payments_historic_list,
            "plans": plans_list
        })
