import uuid
from payments.models import SubscriptionPayment
from .models import SubscriptionPayment
from django.utils.timezone import now, timedelta


def get_idempotent_payment(user, plan, payment_method, interval_minutes=60):
    base_idempotency_key = f"{user.pk}-{plan.uid}-{payment_method}"
    one_hour_ago = now() - timedelta(minutes=interval_minutes)
    existing_payment = SubscriptionPayment.objects.filter(
        idempotency=base_idempotency_key
    ).order_by('-created_at').first()

    if existing_payment and existing_payment.subscription and existing_payment.subscription.plan == plan:
        if existing_payment.status == "paid":
            return existing_payment, True
        elif existing_payment.created_at < one_hour_ago:
            existing_payment.status = False
            existing_payment.save()
            if existing_payment.subscription:
                existing_payment.subscription.status = "expired"
                existing_payment.subscription.save()
            return None, False
        else:
            return existing_payment, True
    return None, False


def create_subscription_payment(user, subscription, payment_method, price, status=False, token=None, gateway_response=None):
    return SubscriptionPayment.objects.create(
        user=user,
        subscription=subscription,
        payment_method=payment_method,
        status=status,
        uid=uuid.uuid4(),
        idempotency=str(uuid.uuid4()),
        token=token,
        price=price,
        gateway_response=gateway_response
    )
