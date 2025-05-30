from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta
from payments.models import UserSubscription, NotificationSend, SubscriptionPayment, PaymentReminderLock
from custom_admin.models import Configuration
from payments.utils import create_subscription_payment
from payments.email_utils import send_subscription_reminder_email
from django.utils import timezone
from django.db import transaction, DatabaseError, IntegrityError

import logging
logger = logging.getLogger('django')

class Command(BaseCommand):
    help = 'Envia lembretes de pagamento para assinaturas próximas do vencimento'

    def handle(self, *args, **kwargs):
        tz = timezone.get_default_timezone()
        today = timezone.localtime(timezone.now(), tz).date()
        try:
            PaymentReminderLock.objects.create(date=today)
        except IntegrityError:
            logger.error("Outro processo já executou o lembrete hoje.")
            return

        try:
            with transaction.atomic():
                config = Configuration.objects.first()
                if not config or not config.days_to_reminder:
                    logger.error('Configuração days_to_reminder não encontrada.')
                    return

                days_to_reminder = config.days_to_reminder
                tz = timezone.get_default_timezone()
                today = timezone.localtime(timezone.now(), tz).date()
                reminder_date = today + timedelta(days=days_to_reminder)

                logger.error(
                    f"Buscando assinaturas que expiram em {reminder_date} (days_to_reminder={days_to_reminder})..."
                )

                subscriptions = UserSubscription.objects.filter(
                    is_active=True,
                    expiration__date=reminder_date
                )

                total = subscriptions.count()
                lembretes_enviados = 0

                if total == 0:
                    logger.error("Nenhuma assinatura encontrada para lembrete.")

                for sub in subscriptions:
                    index = f"email_reminder_{sub.user.uid}"
                    # Verifica se já enviou na data atual
                    if NotificationSend.objects.filter(index=index, date=today).exists():
                        logger.error(f"Lembrete já enviado hoje para {sub.user.email}.")
                        continue

                    # Envia o e-mail de lembrete personalizado
                    try:
                        send_subscription_reminder_email(
                            to_email=sub.user.email,
                            expiration=sub.expiration,
                            user_name=getattr(sub.user, "name", sub.user.email)
                        )
                        lembretes_enviados += 1
                        logger.error(f"Lembrete enviado para {sub.user.email}")
                    except Exception as e:
                        logger.error(f"Erro ao enviar para {sub.user.email}: {str(e)}")

                    # Registra o envio para não duplicar no mesmo dia
                    NotificationSend.objects.create(index=index, date=today)

                    # Cria registro em SubscriptionPayment sem gerar PIX
                    last_payment = SubscriptionPayment.objects.filter(
                        subscription=sub
                    ).order_by('-created_at').first()

                    create_subscription_payment(
                        user=sub.user,
                        subscription=sub,
                        payment_method=last_payment.payment_method if last_payment else "default",
                        price=last_payment.price if last_payment else sub.plan.price,
                        status=False,
                        token=None,
                        gateway_response=None,
                    )
                    logger.error(f"Registro criado em SubscriptionPayment para {sub.user.email}.")

                logger.error(
                    f"Total de lembretes enviados: {lembretes_enviados} de {total} possíveis."
                )
        except DatabaseError:
            logger.error("Outro processo já está executando o lembrete.")
            return
