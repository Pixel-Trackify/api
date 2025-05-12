from django.utils.timezone import now, timedelta
from .models import UserSubscription, SubscriptionPayment
from .gateway import ZeroOneGateway
import hashlib
import uuid


def create_subscription_and_payment(user, plan, payment_method):
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

    gateway_response = ZeroOneGateway.generate_pix_payment(payload)
    raw_key = f"{user.pk}-{plan.uid}-{payment_method}-{uuid.uuid4()}"
    idempotency_key = hashlib.sha256(raw_key.encode()).hexdigest()[:100]

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


def update_payment_status(payment, status):
    """
    Atualiza o estado do pagamento e da assinatura associada.
    """
    if status == "APPROVED":
        # Atualiza o status do pagamento para True
        payment.status = True
        payment.save()

        # Atualiza a assinatura associada
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
