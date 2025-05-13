from .base import PaymentGatewayBase
from custom_admin.models import Configuration
from payments.models import UserSubscription, SubscriptionPayment
from accounts.models import User
from django.conf import settings
from django.utils import timezone
import requests
import uuid
import hashlib
import logging
from datetime import datetime, timedelta

logger = logging.getLogger('django')


class FirebankingGateway(PaymentGatewayBase):
    def generate_payment(self, user, plan, payment_method):
        """
        Cria um pagamento PIX via Firebanking, salva assinatura e pagamento.
        """
        # Gera idempotency_key
        raw_key = f"{user.pk}-{plan.uid}-{payment_method}-{uuid.uuid4()}"
        idempotency_key = hashlib.sha256(raw_key.encode()).hexdigest()[:100]

        try:
            user = User.objects.get(pk=user.pk)
        except User.DoesNotExist:
            raise Exception(f"Usuário não encontrado: {user}")

        config = Configuration.objects.first()
        firebanking_api_key = config.firebanking_api_key

        url = f"{settings.FIRE_BANKING_API_URL}/payment"
        headers = {
            'apiKey': firebanking_api_key,
            'Content-Type': 'application/json',
            'Idempotency-Key': idempotency_key
        }

        data = {
            "type": "PIX",
            "payer": {
                "fullName": user.name,
                "document": user.cpf
            },
            "transaction": {
                "value": int(plan.price * 100),  # Valor em centavos
                "description": f"{plan.name}",
                "dueDate": datetime.now().strftime('%Y-%m-%d'),
                "externalId": idempotency_key
            }
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            gateway_response = response.json()
        except requests.exceptions.RequestException as e:

            raise Exception(
                f"Erro ao criar pagamento PIX: {getattr(e.response, 'text', str(e))}")

        # Cria assinatura e pagamento
        subscription = UserSubscription.objects.create(
            user=user,
            plan=plan,
            is_active=False
        )

        payment = SubscriptionPayment.objects.create(
            uid=uuid.uuid4(),
            idempotency=idempotency_key,
            payment_method=payment_method,
            token=gateway_response.get('transactionId', 'unknown'),
            price=plan.price,
            gateway_response=gateway_response,
            status=False,
            subscription=subscription
        )
        return payment

    def check_pix_payment_status(self, transaction_id):
        """
        Consulta o status de um pagamento PIX na Firebanking.
        """
        url = f"{settings.FIRE_BANKING_API_URL}/payment/{transaction_id}"
        headers = {
            'Authorization': f"Bearer {settings.FIRE_BANKING_API_KEY}"
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(
                f"Erro ao verificar status do pagamento PIX: {getattr(e.response, 'text', str(e))}")

    def update_payment_status(self, payment_uid, status):
        """
        Atualiza o estado do pagamento e da assinatura associada.
        Só ativa se status for PAID.
        """
        try:
            payment = SubscriptionPayment.objects.get(uid=payment_uid)
        except SubscriptionPayment.DoesNotExist:
            return {"error": "Pagamento não encontrado."}

        if status == 'PAID':
            payment.status = True
            payment.save()

            subscription = payment.subscription
            now_time = timezone.now()
            if subscription.expiration and subscription.expiration < now_time:
                subscription.expiration = now_time + timedelta(days=30)
            else:
                subscription.expiration = (
                    subscription.expiration or now_time) + timedelta(days=30)
            # Se existir o campo 'status', usa 'active', senão usa is_active=True
            if hasattr(subscription, 'status'):
                subscription.status = 'active'
            else:
                subscription.is_active = True
            subscription.save()
        else:
            logger.info(f"Status do pagamento não é PAID: {status}")
