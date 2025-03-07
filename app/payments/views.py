from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Subscription, SubscriptionPayment
from .serializers import SubscriptionSerializer, SubscriptionPaymentSerializer
from plans.models import Plan
from django.utils import timezone
from datetime import timedelta
from .fire_banking import create_pix_payment, check_pix_payment_status
from .utils import update_payment_status
import uuid
from django.conf import settings
import logging
import json
import requests


logger = logging.getLogger(__name__)


class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_uid = request.data.get('plan_uid')
        payment_method = request.data.get('payment_method')
        idempotency = request.data.get('idempotency') or str(
            uuid.uuid4())  # Gerar idempotency se não fornecido
        cpf = request.data.get('cpf')

        if not plan_uid or not payment_method:
            logger.error("Parâmetros obrigatórios ausentes")
            return Response({"error": "Parâmetros obrigatórios ausentes."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            plan = Plan.objects.get(uid=plan_uid)
        except Plan.DoesNotExist:
            logger.error("Plano não encontrado")
            return Response({"error": "Plano não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        subscription, created = Subscription.objects.get_or_create(user=request.user, defaults={
            'plan': plan,
            'status': 'pending',
            'expiration': timezone.now() + timedelta(days=30)
        })

        if not created and subscription.status == 'active':
            logger.error("Usuário já possui uma assinatura ativa")
            return Response({"error": "Usuário já possui uma assinatura ativa."}, status=status.HTTP_400_BAD_REQUEST)

        if SubscriptionPayment.objects.filter(idempotency=idempotency).exists():
            logger.error("Pagamento duplicado")
            return Response({"error": "Pagamento duplicado."}, status=status.HTTP_400_BAD_REQUEST)

        x_minutes_ago = timezone.now() - timedelta(minutes=10)
        if SubscriptionPayment.objects.filter(
            user=request.user,
            price=plan.price,
            payment_method=payment_method,
            created_at__gte=x_minutes_ago
        ).exists():
            logger.error("Pagamento duplicado dentro de 10 minutos")
            return Response({"error": "Pagamento duplicado dentro de 10 minutos."}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.cpf and cpf:
            request.user.cpf = cpf
            request.user.save()
        elif not request.user.cpf:
            logger.error("CPF é obrigatório para pagamentos PIX")
            return Response({"error": "CPF é obrigatório para pagamentos PIX."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            pix_response = create_pix_payment(
                plan.price, request.user.cpf, idempotency, request.user, plan)
            payment = SubscriptionPayment.objects.create(
                subscription=subscription,
                idempotency=idempotency,
                payment_method=payment_method,
                token=pix_response['transactionId'],
                price=plan.price,
                status=0,
                user=request.user,
                gateway_response=pix_response
            )
            logger.info("Pagamento PIX criado com sucesso")
            return Response({
                "uid": payment.uid,
                "pixQrCode": pix_response['pixQrCode'],
                "pixCode": pix_response['pixCode'],
                "idempotency": idempotency  # Retornar o idempotency na resposta
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Erro ao criar pagamento PIX: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PaymentStatusCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, uid):
        try:
            payment = SubscriptionPayment.objects.get(
                uid=uid, user=request.user)
            is_paid = payment.status == 1  # Assuming 1 means 'Paid'
            return Response({"status": is_paid}, status=status.HTTP_200_OK)
        except SubscriptionPayment.DoesNotExist:
            return Response({"error": "Pagamento não encontrado ou não pertence ao usuário autenticado."}, status=status.HTTP_404_NOT_FOUND)


class PaymentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, uid):
        try:
            payment = SubscriptionPayment.objects.get(
                uid=uid, user=request.user)
        except SubscriptionPayment.DoesNotExist:
            return Response({"error": "Pagamento não encontrado ou não pertence ao usuário autenticado."}, status=status.HTTP_404_NOT_FOUND)

        try:
            pix_status = check_pix_payment_status(payment.token)
            return Response({"status": pix_status['status'] == 'PAID'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PaymentWebhookView(APIView):
    def post(self, request):
        try:
            # Decodificar o JSON recebido no corpo da requisição
            encoded_data = json.loads(request.body)
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON payload."}, status=status.HTTP_400_BAD_REQUEST)

        # Extrair os campos relevantes do JSON
        transaction_id = encoded_data.get('transactionId')
        payment_uid = encoded_data.get('businessTransactionId')
        payment_status = encoded_data.get('status')

        # Verificar se os campos obrigatórios estão presentes
        if not payment_uid or not payment_status:
            return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Garantir que payment_uid é um UUID válido
            payment_uid = uuid.UUID(payment_uid)
        except ValueError:
            return Response({"error": "UUID inválido."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Buscar o pagamento na tabela SubscriptionPayment
            payment = SubscriptionPayment.objects.get(
                uid=payment_uid, status=0)  # Assuming 0 means 'Pending'
        except SubscriptionPayment.DoesNotExist:
            return Response({"error": "Pagamento não encontrado ou já processado."}, status=status.HTTP_404_NOT_FOUND)

        if payment_status == 'PAID':
            # Atualizar o status do pagamento para 'Paid'
            payment.status = 1  # Assuming 1 means 'Paid'
            payment.save()

            # Enviar email para o cliente

            return Response({"status": "Pagamento atualizado e email enviado."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Status de pagamento inválido."}, status=status.HTTP_400_BAD_REQUEST)


class TransactionStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            # Garantir que id é um UUID válido
            transaction_id = uuid.UUID(str(id))
        except ValueError:
            return Response({"error": "UUID inválido."}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar o pagamento na tabela SubscriptionPayment e garantir que pertence ao usuário autenticado
        try:
            payment = SubscriptionPayment.objects.get(
                token=transaction_id, user=request.user)
        except SubscriptionPayment.DoesNotExist:
            return Response({"error": "Pagamento não encontrado ou não pertence ao usuário autenticado."}, status=status.HTTP_404_NOT_FOUND)

        # Fazer a requisição para o endpoint do provedor de pagamento
        url = f"{settings.FIRE_BANKING_API_URL}/transactions/{transaction_id}"
        headers = {
            'apiKey': f"{settings.FIRE_BANKING_API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({"error": "Erro ao consultar o provedor de pagamento."}, status=status.HTTP_400_BAD_REQUEST)

        transaction_data = response.json()

        # Verificar o estado da transação
        if transaction_data['operation']['status'] == 'PAID':
            payment.status = 1  # Assuming 1 means 'Paid'
            payment.save()

            # Atualizar a data de expiração da assinatura
            subscription = payment.subscription
            current_time = timezone.now()
            if subscription.expiration < current_time:
                subscription.expiration = current_time + \
                    timezone.timedelta(days=30)
            else:
                subscription.expiration += timezone.timedelta(days=30)
            subscription.status = 'active'
            subscription.save()

            # Enviar email para o cliente

            return Response({"status": "Pagamento atualizado e assinatura renovada."}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "Pagamento ainda não foi realizado."}, status=status.HTTP_200_OK)
