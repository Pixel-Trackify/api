from django.utils.timezone import now, timedelta


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

            subscription.is_active = True
            subscription.save()
