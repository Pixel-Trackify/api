from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta
from payments.models import UserSubscription, NotificationSend
from custom_admin.models import Configuration
from payments.email_utils import send_subscription_reminder_email


class Command(BaseCommand):
    help = 'Envia lembretes de pagamento para assinaturas próximas do vencimento'

    def handle(self, *args, **kwargs):
        config = Configuration.objects.first()
        if not config or not config.days_to_reminder:
            self.stdout.write(self.style.WARNING(
                'Configuração days_to_reminder não encontrada.'))
            return

        days_to_reminder = config.days_to_reminder
        today = now().date()
        reminder_date = today + timedelta(days=days_to_reminder)

        subscriptions = UserSubscription.objects.filter(
            is_active=True,
            expiration__date=reminder_date
        )

        for sub in subscriptions:
            index = f"email_reminder_{sub.user.id}"
            # Verifica se já enviou hoje
            if NotificationSend.objects.filter(index=index, date=today).exists():
                continue

            # Envia o e-mail de lembrete personalizado
            send_subscription_reminder_email(
                to_email=sub.user.email,
                user_name=getattr(sub.user, "name", sub.user.email)
            )

            # Registra o envio para não duplicar no mesmo dia
            NotificationSend.objects.create(index=index, date=today)
            self.stdout.write(self.style.SUCCESS(
                f"Lembrete enviado para {sub.user.email}"))
