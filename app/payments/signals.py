from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserSubscription
from accounts.utils import sync_user_subscription


@receiver(post_save, sender=UserSubscription)
def update_user_subscription_on_save(sender, instance, **kwargs):
    """
    Atualiza os campos subscription_active e subscription_expiration do usuário
    após salvar uma assinatura.
    """
    sync_user_subscription(instance.user)
