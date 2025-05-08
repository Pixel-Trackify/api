from django.utils.timezone import now
from zeroone_payments.models import UserSubscription


def sync_user_subscription(user):
    """
    Sincroniza os campos subscription_active e subscription_expiration
    do modelo Usuario com base nos dados de UserSubscription.
    """
    # Busca todas as assinaturas do usuário
    subscriptions = UserSubscription.objects.filter(user=user)

    if subscriptions.exists():
        # Obtém a assinatura com a maior data de expiração
        latest_subscription = subscriptions.order_by('-expiration').first()

        # Verifica se a assinatura está ativa e não expirou
        if latest_subscription.is_active and latest_subscription.expiration > now():
            user.subscription_active = True
            user.subscription_expiration = latest_subscription.expiration
        else:
            # Assinatura expirada ou inativa
            user.subscription_active = False
            user.subscription_expiration = None
    else:
        # Caso o usuário não tenha nenhuma assinatura
        user.subscription_active = False
        user.subscription_expiration = None

    # Salva as alterações no modelo Usuario
    user.save()
