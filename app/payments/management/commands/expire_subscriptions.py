from django.core.management.base import BaseCommand
from django.utils.timezone import now
from payments.models import UserSubscription
from accounts.utils import sync_user_subscription
from accounts.models import Usuario


class Command(BaseCommand):
    help = 'Desativa assinaturas vencidas'

    def handle(self, *args, **kwargs):
        now_time = now()
        expired = UserSubscription.objects.filter(
            is_active=True,
            expiration__isnull=False,
            expiration__lte=now_time
        )
        user_ids = list(expired.values_list(
            'user_id', flat=True).distinct())
        count = expired.update(is_active=False, status='expired')
        self.stdout.write(self.style.SUCCESS(
            f'{count} assinaturas expiradas/desativadas.'))

        # Sincroniza os usuários afetados
        for user_id in user_ids:
            user = Usuario.objects.get(pk=user_id)
            sync_user_subscription(user)
            user.refresh_from_db()
            self.stdout.write(self.style.SUCCESS(
                f"Usuário {user.pk} | "
            ))

        self.stdout.write(self.style.SUCCESS(
            f"{len(user_ids)} usuários sincronizados após expiração de assinaturas."
        ))
