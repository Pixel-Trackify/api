from .base import PaymentGatewayBase
from custom_admin.models import Configuration
from payments.models import UserSubscription, SubscriptionPayment
from django.utils.timezone import now, timedelta
from decimal import Decimal, ROUND_HALF_UP
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
                f"{settings.ZEROONE_API_URL}transaction.purchase", json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao comunicar com o gateway ZeroOne: {str(e)}")
            raise Exception(
                f"Erro ao comunicar com o gateway ZeroOne: {str(e)}")

    def create_subscription_and_payment(self, user, plan, payment_method, idempotency_key=None):
        config = Configuration.objects.first()
        late_interest = config.late_payment_interest or 0
        daily_late_interest = config.daily_late_payment_interest or 0

        subscription, created = UserSubscription.objects.get_or_create(
            user=user,
            defaults={
                "plan": plan,
                "is_active": False
            }
        )

        if not created:
            # Atualiza a assinatura existente
            subscription.plan = plan
            subscription.is_active = False
            subscription.save()

        # Valor base do plano
        price = Decimal(str(plan.price))

        # Cálculo de juros por atraso, se ativado
        if not created and subscription.expiration:
            expiration_date = subscription.expiration.date() if hasattr(
                subscription.expiration, 'date') else subscription.expiration
            today = now().date()
            if expiration_date < today and (late_interest > 0 or daily_late_interest > 0):
                juros = Decimal('0.00')
                if late_interest > 0:
                    juros = (Decimal(str(late_interest)) /
                             Decimal('100')) * price
                dias_atraso = (today - expiration_date).days
                juros_diario = Decimal('0.00')
                if daily_late_interest > 0:
                    juros_diario = (Decimal(str(daily_late_interest)) /
                                    Decimal('100')) * price * dias_atraso
                price += juros + juros_diario

        # Arredonda para 2 casas decimais
        price = price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        payload = {
            "name": user.name,
            "email": user.email,
            "cpf": user.cpf,
            "phone": getattr(user, 'phone', "00000000000"),
            "paymentMethod": payment_method,
            "amount": int(price * 100),  # valor final em centavos
            "items": [
                {
                    "unitPrice": int(price * 100),
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

        # Busca ou cria o pagamento
        payment, created = SubscriptionPayment.objects.get_or_create(
            subscription=subscription,
            payment_method=payment_method,
            status=False,
            defaults={
                "uid": uuid.uuid4(),
                "idempotency": idempotency_key,
                "token": gateway_response.get('id', 'zeroone'),
                "price": price,  # Usa Decimal!
                "gateway_response": gateway_response,
            }
        )

        if not created:
            # Atualiza o pagamento existente
            payment.idempotency = idempotency_key
            payment.token = gateway_response.get('id', 'zeroone')
            payment.price = price  # Usa Decimal!
            payment.gateway_response = gateway_response
            payment.created_at = now()
            payment.save()

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
