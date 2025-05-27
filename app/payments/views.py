from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from plans.models import Plan
from .models import SubscriptionPayment, UserSubscription
from custom_admin.models import Configuration
from .serializers import PaymentSerializer, SubscriptionPlanSerializer, PlanInfoSerializer, PaymentOpenedSerializer, PaymentHistoricSerializer
from django.utils.timezone import now, timedelta
from .utils import get_idempotent_payment
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from .gateways import get_gateway
from .schemas import payment_status_schema, payment_create_schema, payment_webhook_schema, payment_change_plan_schema, subscription_info_schema
import uuid
import hashlib
import requests
import logging
import os
from django.conf import settings

logger = logging.getLogger('django')


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
        """
        1) Verificar o tipo de pagamento (plan_uid, paymentMethod, gateway ou uid )
            UID é da tabela subscription_payment (deve pertencer ao mesmo usuário da request), caso esse parametro seja passado, o plan_uid e paymentMethod não devem ser passados.
            verificar se o usuário já gerou um pagamento e está em aberto no intervalo de 1 hora, se sim, retornar o pagamento existente.
            se não existir, geralmente no cenário que gera o pagamento via cron, deve gerar o pagamento normalmente. 
             
             

        2) Se não for passado o uid, deve validar os parametros plan_uid, paymentMethod e gateway.
           Geralmente é usado para escolher um plano e gerar o pagamento. 
           Segue a lógica como está atualmente, se houver uma assinatura seja ativa ou não vai remove-la, e vai editar os pagamentos existentes para subscription_id = NULL.
           
           Aqui tbm segue a mesma lógica de idempotência, se o usuário já tiver um pagamento em aberto no intervalo de 1 hora, deve retornar o pagamento existente.
           Caso não exista, deve gerar o pagamento normalmente.
        
        """  
        user = request.user
        uid = request.data.get('uid')
        # Primeiro cenário, pode ser pagar uma fatura aberta ou gerar um novo pagamento ( Cenário quando o cron gera o pagamento ou quando o usuário fecha a tela do QR Code )
        if uid:
            logger.info(f"Usuário {user} solicitou pagamento com UID: {uid}")
            try:
               
                payment = SubscriptionPayment.objects.get(uid=uid, subscription__user=user, status=False)
            except SubscriptionPayment.DoesNotExist:
                return Response({"error": "Pagamento não encontrado."}, status=status.HTTP_404_NOT_FOUND)

            # Verifica se o pagamento está em aberto e dentro do intervalo de 1 hora
            if (payment.gateway_response and payment.token and now() - payment.created_at) < timedelta(hours=1):
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
                }, status=status.HTTP_200_OK) 
            
            plan = payment.subscription.plan if payment.subscription.plan else None
            data = {
                "paymentMethod": payment.payment_method if payment.payment_method else 'PIX',
                "gateway": payment.gateway if payment.gateway else 'zeroone',
            }
        else:        
           # try:
           #     plan = Plan.objects.get(uid=data['plan_uid'])
           # except Plan.DoesNotExist:
           #     return Response({"error": "Plano não encontrado."}, status=status.HTTP_404_NOT_FOUND)
            serializer = PaymentSerializer(
                data=request.data, context={'request': request})
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            data = serializer.validated_data
            plan = data['plan']
            # Checagem de idempotência via utilitário
            existing_payment, is_recent = get_idempotent_payment(user, plan, data['paymentMethod'])
            if is_recent and existing_payment:
                return Response({
                    "message": "Pagamento criado com sucesso.",
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
                user, plan, data['paymentMethod']
            )
            payment.gateway = gateway_name
            payment.user = user
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

        # Checagem de idempotência
        existing_payment, is_recent = get_idempotent_payment(
            user, plan, data['paymentMethod'])
        if is_recent and existing_payment:
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

        # Exclui assinatura atual do usuário
        SubscriptionPayment.objects.filter(
            subscription__user=user,
            status=False
        ).delete()
        
        SubscriptionPayment.objects.filter(
            subscription__user=user,
            status=True
        ).update(subscription=None)

        UserSubscription.objects.filter(
            user=user
        ).delete()

        try:
            gateway_name = data['gateway']
            gateway = get_gateway(gateway_name)
            payment = gateway.generate_payment(
                user, plan, data['paymentMethod'])
            payment.gateway = gateway_name
            payment.user = user
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


class SubscriptionInfoView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**subscription_info_schema)
    def get(self, request):
        user = request.user

        # Assinatura do usuário
        subscription = UserSubscription.objects.filter(
            user=user
        ).select_related('plan').order_by('-expiration').first()
        plan_data = SubscriptionPlanSerializer(
            subscription).data if subscription else {}

        # Pagamentos em aberto
        payment_opened = SubscriptionPayment.objects.filter(
            subscription__user=user, status=False
        ).order_by('-created_at')
        payments_opened_list = PaymentOpenedSerializer(
            payment_opened, many=True).data

        # Histórico de pagamentos pagos
        payments_historic = SubscriptionPayment.objects.filter(
            user=user, status=True
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


class PaymentWebhookView(APIView):
    """
    Endpoint para processar notificações do gateway de pagamento.
    """
    @extend_schema(**payment_webhook_schema)
    def post(self, request):
        data = request.data

        payment_id = data.get("paymentId")
        if not payment_id:
            return Response({"error": "Dados inválidos."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = SubscriptionPayment.objects.get(token=payment_id)
        except SubscriptionPayment.DoesNotExist:
            return Response({"error": "Pagamento não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Verifica se está em produção, se não, o estado do pagamento vem no payload
        if bool(int(os.getenv('DEBUG', 0))):
            payment_status = data.get("status")
            if not payment_status:
                return Response({"error": "Status não informado no payload."}, status=status.HTTP_400_BAD_REQUEST)

            payment_data = {
                "status": payment_status,
            }

        else:
            zeroone_config = Configuration.objects.first()
            if not zeroone_config or not zeroone_config.zeroone_secret_key:
                return Response({"error": "Chave de autorização ZeroOne não configurada."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            zeroone_secret_key = zeroone_config.zeroone_secret_key

            # Consulta o status do pagamento na API ZeroOne
            url = f"{settings.ZEROONE_API_URL}transaction.getPayment/"
            params = {"id": payment.token}
            headers = {"Authorization": zeroone_secret_key}
            response = requests.get(url, params=params, headers=headers)
            if response.status_code != 200:
                return Response({"error": "Erro ao consultar status na ZeroOne."}, status=status.HTTP_502_BAD_GATEWAY)

            payment_data = response.json()
            payment_status = payment_data.get("status")

            if not payment_status:
                return Response({"error": "Resposta inválida da ZeroOne."}, status=status.HTTP_502_BAD_GATEWAY)

        # Atualiza o status do pagamento no sistema
        gateway_name = payment.gateway
        gateway = get_gateway(gateway_name)
        gateway.update_payment_status(payment.uid, payment_status)

        return Response(payment_data, status=status.HTTP_200_OK)
