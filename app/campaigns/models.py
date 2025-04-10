from django.db import models
from integrations.models import Integration, User
import uuid
from decimal import Decimal


class Campaign(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    integrations = models.ManyToManyField(
        Integration, related_name='campaigns')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='campaigns', default=1)
    source = models.CharField(max_length=100, default='Kwai')
    title = models.CharField(max_length=255)
    CPM = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, default=None
    )
    CPC = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, default=None
    )
    CPV = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, default=None
    )

    METHOD_CHOICES = [
        ('CPM', 'CPM'),
        ('CPC', 'CPC'),
        ('CPV', 'CPV'),
    ]
    method = models.CharField(
        max_length=3, choices=METHOD_CHOICES, null=True, blank=True, default=None
    )
    total_approved = models.IntegerField(default=0)
    total_pending = models.IntegerField(default=0)
    amount_approved = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    amount_pending = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    total_ads = models.DecimalField(max_digits=13, decimal_places=8, default=0)
    profit = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    ROI = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    total_views = models.IntegerField(default=0)
    total_clicks = models.IntegerField(default=0)
    total_abandoned = models.IntegerField(default=0)
    amount_abandoned = models.DecimalField(
        max_digits=15, decimal_places=2, default=0)
    total_canceled = models.IntegerField(default=0)
    amount_canceled = models.DecimalField(
        max_digits=15, decimal_places=2, default=0)
    total_refunded = models.IntegerField(default=0)
    amount_refunded = models.DecimalField(
        max_digits=15, decimal_places=2, default=0)
    total_rejected = models.IntegerField(default=0)
    amount_rejected = models.DecimalField(
        max_digits=15, decimal_places=2, default=0)
    total_chargeback = models.IntegerField(default=0)
    amount_chargeback = models.DecimalField(
        max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campaigns'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Atualiza o campo `in_use` das integrações associadas ao salvar a campanha.
        """
        super().save(*args, **kwargs)  # Salva a campanha primeiro
        # Atualiza o campo `in_use` para todas as integrações associadas
        for integration in self.integrations.all():
            integration.in_use = True
            integration.save()

    def delete(self, *args, **kwargs):
        """
        Atualiza o campo `in_use` das integrações associadas ao excluir a campanha.
        """
        # Atualiza o campo `in_use` para todas as integrações associadas antes de excluir
        for integration in self.integrations.all():
            integration.in_use = False
            integration.save()
        super().delete(*args, **kwargs)  # Exclui a campanha


class CampaignView(models.Model):
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name='views')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user_agent = models.TextField()
    ip_address = models.GenericIPAddressField()
    action = models.CharField(max_length=10)  # 'view' ou 'click'

    class Meta:
        db_table = 'campaign_views'

    def __str__(self):
        return f"{self.campaign.title} - {self.action} - {self.created_at}"


class FinanceLogs(models.Model):
    id = models.AutoField(primary_key=True)
    campaign = models.ForeignKey(
        'Campaign', on_delete=models.CASCADE, related_name='finance_logs', default=0
    )
    profit = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    ROI = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    total_views = models.IntegerField(default=0)
    total_clicks = models.IntegerField(default=0)
    total_ads = models.DecimalField(max_digits=13, decimal_places=8, default=0)
    total_approved = models.IntegerField(default=0)
    total_pending = models.IntegerField(default=0)
    total_refunded = models.IntegerField(default=0)
    total_abandoned = models.IntegerField(default=0)
    total_chargeback = models.IntegerField(default=0)
    total_rejected = models.IntegerField(default=0)
    amount_approved = models.DecimalField(
        max_digits=15, decimal_places=2, default=0)
    amount_pending = models.DecimalField(
        max_digits=15, decimal_places=2, default=0)
    amount_refunded = models.DecimalField(
        max_digits=15, decimal_places=2, default=0)
    amount_rejected = models.DecimalField(
        max_digits=15, decimal_places=2, default=0)
    amount_chargeback = models.DecimalField(
        max_digits=15, decimal_places=2, default=0)
    amount_abandoned = models.DecimalField(
        max_digits=15, decimal_places=2, default=0)
    date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'finances_logs'
        # Garante que não existam duplicatas para a mesma campanha e data
        unique_together = ('campaign', 'date')
        indexes = [
            # Índice para consultas rápidas
            models.Index(fields=['campaign', 'date']),
        ]

    def __str__(self):
        return f"FinanceLogs for Campaign {self.campaign.id} on {self.date}"
