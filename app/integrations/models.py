from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.utils import timezone

User = get_user_model()


class Integration(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='integrations')
    name = models.CharField(max_length=255)
    gateway = models.CharField(max_length=255, choices=[
        ('zeroone', 'ZeroOne'),
        ('ghostspay', 'GhostsPay'),
        ('paradisepag', 'ParadisePag'),
        ('disrupty', 'Disrupty'),
        ('wolfpay', 'WolfPay'),
        ('vegacheckout', 'VegaCheckout'),
        ('cloudfy', 'CloudFy'),
        ('tribopay', 'TriboPay'),
        ('westpay', 'WestPay'),
        ('sunize', 'Sunize'),
        ('grapefy', 'Grapefy'),


    ])
    in_use = models.BooleanField(default=False) 
    deleted = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=[(
        'active', 'Active'), ('inactive', 'Inactive')], default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.pk:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'integrations'


class IntegrationRequest(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    integration = models.ForeignKey(
        Integration, on_delete=models.CASCADE, related_name='requests')
    status = models.CharField(max_length=20)
    payment_id = models.CharField(max_length=255)
    payment_method = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    response = models.JSONField()
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'integrations_requests'


class IntegrationSample(models.Model):
    id = models.AutoField(primary_key=True)
    gateway = models.CharField(max_length=255, unique=True)
    response = models.JSONField()
    timestamp = models.DateTimeField(
        auto_now_add=True)

    def __str__(self):
        return f"Sample for {self.gateway}"

    class Meta:
        db_table = 'integration_samples'


class Transaction(models.Model):
    METHOD_CHOICES = [
        ('PIX', 'PIX'),
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
        ('Boleto', 'Boleto'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('REFUNDED', 'Refunded'),
        ('CHARGEBACK', 'Chargeback'),
    ]

    id = models.AutoField(primary_key=True)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    integration = models.ForeignKey(
        Integration, on_delete=models.CASCADE, related_name='transactions')
    transaction_id = models.CharField(max_length=255, unique=True)
    method = models.CharField(
        max_length=20, choices=METHOD_CHOICES, default='PIX')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='PENDING')
    data_response = models.JSONField(default=dict)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __str__(self):
        return self.transaction_id

    class Meta:
        db_table = 'transactions'
