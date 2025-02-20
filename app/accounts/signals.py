from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
from django.utils.timezone import now
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(user_login_failed)
def register_failed_login(sender, credentials, **kwargs):
    identifier = credentials.get("identifier")

    if not identifier:
        return

    user = None
    if "@" in identifier:
        user = User.objects.filter(email=identifier).first()
    elif identifier.isdigit() and len(identifier) in [11, 14]:
        user = User.objects.filter(cpf=identifier).first()

    if user:
        user.increment_login_attempts()
