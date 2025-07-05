from django.core.management.base import BaseCommand
from django.utils.timezone import now
from payments.models import UserSubscription
from accounts.utils import sync_user_subscription
from accounts.models import Usuario
from payments.models import PaymentExpireLock
from django.utils import timezone
from django.db import transaction, DatabaseError, IntegrityError
import logging
logger = logging.getLogger('django')

class Command(BaseCommand):
    help = 'Desativa assinaturas vencidas'

    def handle(self, *args, **kwargs):
        tz = timezone.get_default_timezone()
        today = timezone.localtime(timezone.now(), tz).date()
        
        try:
            PaymentExpireLock.objects.create(date=today)
        except IntegrityError:
            logger.error("Outro processo já executou o marcar como expirado hoje.")
            return
        
        try:
            with transaction.atomic():
                expired = UserSubscription.objects.filter(
                    is_active=True,
                    expiration__isnull=False,
                    expiration__date=today  # Busca por data de expiração igual a hoje
                )
                user_ids = list(expired.values_list(
                    'user_id', flat=True).distinct())
                count = expired.update(is_active=False, status='expired')
                
                logger.info(f'{count} assinaturas expiradas/desativadas.')

                # Sincroniza os usuários afetados
                for user_id in user_ids:
                    user = Usuario.objects.get(pk=user_id)
                    sync_user_subscription(user)
                    user.refresh_from_db()
                    
                    logger.info(f"Usuário {user.pk} | ") 

                logger.info(f"{len(user_ids)} usuários sincronizados após expiração de assinaturas.") 
        except DatabaseError:
            logger.error("Outro processo já está executando o expirar assinatura.")
            return
