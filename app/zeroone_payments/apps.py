from django.apps import AppConfig


class ZeroOnePaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'zeroone_payments'

    def ready(self):
        import zeroone_payments.signals  
