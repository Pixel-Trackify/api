from django.utils.timezone import now
from payments.models import UserSubscription


def sync_user_subscription(user):
    """
    Sincroniza os campos subscription_active e subscription_expiration
    do modelo Usuario com base nos dados de UserSubscription.
    """
    subscriptions = UserSubscription.objects.filter(user=user)

    if subscriptions.exists():
        latest_subscription = subscriptions.order_by('-expiration').first()

        if latest_subscription.is_active and latest_subscription.expiration > now():
            user.subscription_active = True
        else:
            user.subscription_active = False

        user.subscription_expiration = latest_subscription.expiration
    else:
        user.subscription_active = False
        user.subscription_expiration = None

    user.save()
