from django.core.management.base import BaseCommand
from django.utils.timezone import now
from payments.models import UserSubscription


class Command(BaseCommand):
    help = 'Desativa assinaturas vencidas'

    def handle(self, *args, **kwargs):
        now_time = now()
        expired = UserSubscription.objects.filter(
            is_active=True,
            expiration__isnull=False,
            expiration__lte=now_time
        )
        count = expired.update(is_active=False, status='expired')
        self.stdout.write(self.style.SUCCESS(
            f'{count} assinaturas expiradas/desativadas.'))
