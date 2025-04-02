from django.db.models.signals import post_save
from django.dispatch import receiver
from campaigns.models import Campaign  # Importar o modelo Campaign corretamente


@receiver(post_save, sender=Campaign)
def update_user_profit(sender, instance, **kwargs):
    """
    Atualiza o profit do usuário sempre que uma campanha for salva.
    """
    if instance.user:  # Certifique-se de que a campanha está associada a um usuário
        instance.user.recalculate_profit()
