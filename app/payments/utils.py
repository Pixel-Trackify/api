from django.utils import timezone
from datetime import timedelta
from .models import SubscriptionPayment, Subscription


def update_payment_status(payment_uid, status):
    try:
        payment = SubscriptionPayment.objects.get(uid=payment_uid)
    except SubscriptionPayment.DoesNotExist:
        return {"error": "Pagamento não encontrado."}

    if status == 'PAID':
        payment.status = 1
        payment.save()

        subscription = payment.subscription
        if subscription.expiration and subscription.expiration < timezone.now():
            subscription.expiration = timezone.now() + timedelta(days=30)
        else:
            subscription.expiration += timedelta(days=30)
        subscription.status = 'active'
        subscription.save()

        # Enviar email para o cliente (simulação)
        print(
            f"Email enviado para {subscription.user.email} confirmando o pagamento.")

    return {"message": "Status do pagamento atualizado com sucesso."}
