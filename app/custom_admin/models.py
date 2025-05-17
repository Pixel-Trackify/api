from django.db import models


class Configuration(models.Model):
    PIX_CHOICES = [
        ('zeroone', 'ZeroOne'),
        ('firebanking', 'Firebanking'),
    ]
    updated_at = models.DateTimeField(auto_now=True)
    email_register_subject = models.CharField(max_length=250)
    email_recovery_subject = models.CharField(max_length=250)
    email_reminder_subject = models.CharField(max_length=250)
    email_expired_subject = models.CharField(max_length=250)
    email_subscription_paid_subject = models.CharField(max_length=250)
    email_register = models.TextField()
    email_recovery = models.TextField()
    email_reminder = models.TextField()
    email_expired = models.TextField()
    email_subscription_paid = models.TextField()
    require_email_confirmation = models.BooleanField(default=False)
    default_pix = models.CharField(
        max_length=20,
        choices=PIX_CHOICES,
        default='zeroone'
    )
    firebanking_api_key = models.TextField(null=True, blank=True)
    zeroone_webhook = models.TextField(null=True, blank=True)
    zeroone_webhook_code = models.TextField(null=True, blank=True)
    zeroone_secret_key = models.TextField(null=True, blank=True)
    recaptchar_enable = models.BooleanField(default=False)
    recaptchar_site_key = models.CharField(max_length=250)
    recaptchar_secret_key = models.CharField(max_length=250)
    days_to_reminder = models.IntegerField()
    days_to_expire = models.IntegerField()
    late_payment_interest = models.FloatField(default=2.0)
    daily_late_payment_interest = models.FloatField(default=0.0333)

    def __str__(self):
        return f"Configuration {self.id}"

    class Meta:
        db_table = 'adm_configuration'
