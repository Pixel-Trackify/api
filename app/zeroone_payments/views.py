from rest_framework.views import APIView
from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from plans.models import Plan
from .models import SubscriptionPayment, UserSubscription
from .serializers import PaymentSerializer
from .gateway import ZeroOneGateway
from .utils import update_payment_status
from django.utils.timezone import now, timedelta
import uuid
from drf_spectacular.utils import extend_schema
from .schemas import payment_status_schema, payment_create_schema, payment_webhook_schema


class PaymentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**payment_status_schema)
    def get(self, request, uid):
        payment = get_object_or_404(SubscriptionPayment, uid=uid)

        return Response({"status": payment.status}, status=status.HTTP_200_OK)


class PaymentView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**payment_create_schema)
    def post(self, request):
        serializer = PaymentSerializer(
            data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        user = request.user

        # Busca o plano no banco de dados com base no plan_uid
        try:
            plan = Plan.objects.get(uid=data['plan_uid'])
        except Plan.DoesNotExist:
            return Response({"error": "Plano não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Gera a chave de idempotência
        idempotency_key = f"{user.pk}-{plan.uid}-{data['paymentMethod']}"

        # Verifica se já existe um pagamento recente com a mesma idempotência
        one_hour_ago = now() - timedelta(minutes=60)
        existing_payment = SubscriptionPayment.objects.filter(
            idempotency=idempotency_key,
            created_at__gte=one_hour_ago
        ).order_by('-created_at').first()

        # Se existir um pagamento recente e o plano não foi alterado, retorna o pagamento existente
        if existing_payment and existing_payment.subscription.plan == plan:
            return Response({
                "message": "Pagamento já processado recentemente.",
                "payment": {
                    "uid": existing_payment.uid,
                    "status": existing_payment.status,
                    "price": existing_payment.price,
                    "payment_method": existing_payment.payment_method,
                    "gateway_response": existing_payment.gateway_response

                }
            }, status=status.HTTP_200_OK)

        # payload para o gateway
        payload = {
            "name": user.name,
            "email": user.email,
            "cpf": user.cpf,
            "phone": user.phone if hasattr(user, 'phone') else "00000000000",
            "paymentMethod": data['paymentMethod'],
            "amount": int(plan.price * 100),
            "items": [
                {
                    "unitPrice": int(plan.price * 100),
                    "title": str(plan.uid),
                    "quantity": 1,
                    "tangible": False
                }
            ]
        }

        # Envia a requisição ao gateway
        try:
            gateway_response = ZeroOneGateway.generate_pix_payment(payload)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Cria ou atualiza a assinatura do usuário
        # Tenta buscar a assinatura existente
        subscription = UserSubscription.objects.filter(
            user=user, plan=plan).first()

        if not subscription:

            subscription = UserSubscription(
                user=user, plan=plan, is_active=False)
            subscription.save()
            subscription.expiration = subscription.calculate_end_date()
            subscription.save()
        else:

            subscription.expiration = subscription.calculate_end_date()
            subscription.is_active = False
            subscription.save()

        # Cria a requisição de pagamento
        payment = SubscriptionPayment.objects.create(
            uid=uuid.uuid4(),
            idempotency=idempotency_key,
            payment_method=data['paymentMethod'],
            token=gateway_response.get('id', 'unknown'),
            price=plan.price,
            gateway_response=gateway_response,
            status=False,
            subscription=subscription
        )
        return Response({
            "message": "Pagamento criado com sucesso.",
            "payment": {
                "uid": payment.uid,
                "status": payment.status,
                "price": payment.price,
                "payment_method": payment.payment_method,
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

        # Atualiza o estado do pagamento e da assinatura
        update_payment_status(payment, payment_status)

        return Response({"message": "Estado do pagamento atualizado com sucesso."}, status=status.HTTP_200_OK)
