from django.utils import timezone
from datetime import timedelta
from .models import SubscriptionPayment

def update_payment_status(payment_uid, status):
    try:
        payment = SubscriptionPayment.objects.get(uid=payment_uid)
    except SubscriptionPayment.DoesNotExist:
        return {"error": "Pagamento não encontrado."}

    payment.status = 1 if status == 'paid' else 0
    payment.save()

    if status == 'paid':
        subscription = payment.subscription
        subscription.status = 'active'
        subscription.expiration = timezone.now() + timedelta(days=30)
        subscription.save()

        # Enviar email para o cliente (simulação)
        print(f"Email enviado para {subscription.user.email} confirmando o pagamento.")

    return {"message": "Status do pagamento atualizado com sucesso."}