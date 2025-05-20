from .base import PaymentGatewayBase
from custom_admin.models import Configuration
from payments.models import UserSubscription, SubscriptionPayment
from django.utils.timezone import now, timedelta
import requests
import hashlib
import uuid
import logging
from django.conf import settings

logger = logging.getLogger('django')


class ZeroOneGateway(PaymentGatewayBase):
    def generate_payment(self, user, plan, payment_method, idempotency_key=None):
        """
        Compatível com o seletor dinâmico de gateways.
        """
        return self.create_subscription_and_payment(user, plan, payment_method, idempotency_key)

    def generate_pix_payment(self, payload):
        config = Configuration.objects.first()
        if not config or not config.zeroone_secret_key:
            raise Exception("Chave ZeroOne não encontrada.")
        zeroone_secret_key = config.zeroone_secret_key

        headers = {
            'Authorization': zeroone_secret_key,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(
                settings.ZEROONE_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao comunicar com o gateway ZeroOne: {str(e)}")
            raise Exception(
                f"Erro ao comunicar com o gateway ZeroOne: {str(e)}")

    def create_subscription_and_payment(self, user, plan, payment_method, idempotency_key=None):
        subscription = UserSubscription.objects.create(
            user=user,
            plan=plan,
            is_active=False
        )

        payload = {
            "name": user.name,
            "email": user.email,
            "cpf": user.cpf,
            "phone": getattr(user, 'phone', "00000000000"),
            "paymentMethod": payment_method,
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

        gateway_response = self.generate_pix_payment(payload)
        if not idempotency_key:
            raw_key = f"{user.pk}-{plan.uid}-{payment_method}-{uuid.uuid4()}"
            idempotency_key = hashlib.sha256(
                raw_key.encode()).hexdigest()[:100]

        payment = SubscriptionPayment.objects.create(
            uid=uuid.uuid4(),
            idempotency=idempotency_key,
            payment_method=payment_method,
            token=gateway_response.get('id', 'unknown'),
            price=plan.price,
            gateway_response=gateway_response,
            status=False,
            subscription=subscription
        )
        return payment

    def update_payment_status(self, payment_uid, status):
        """
        Atualiza o estado do pagamento e da assinatura associada.
        """
        try:
            payment = SubscriptionPayment.objects.get(uid=payment_uid)
        except SubscriptionPayment.DoesNotExist:
            return {"error": "Pagamento não encontrado."}

        if status == "APPROVED":
            payment.status = True
            payment.save()

            subscription = payment.subscription
            if subscription:
                current_time = now()
                if subscription.expiration and subscription.expiration > current_time:
                    subscription.expiration += timedelta(
                        days=30 * subscription.plan.duration_value)
                else:
                    subscription.expiration = current_time + \
                        timedelta(days=30 * subscription.plan.duration_value)

                # Desativa todas as outras assinaturas ativas do usuário
                UserSubscription.objects.filter(
                    user=subscription.user, is_active=True
                ).exclude(pk=subscription.pk).update(is_active=False)

                subscription.is_active = True
                subscription.save()
