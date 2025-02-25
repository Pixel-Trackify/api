from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Integration(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='integrations')
    name = models.CharField(max_length=255)
    platform = models.CharField(max_length=100, default='ZeroOne')
    credentials = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'integrations'


class Transaction(models.Model):
    METHOD_CHOICES = [
        ('PIX', 'PIX'),
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
        ('Boleto', 'Boleto'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
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
        max_length=20, choices=STATUS_CHOICES, default='pending')
    data_response = models.JSONField(default=dict)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __str__(self):
        return self.transaction_id

    class Meta:
        db_table = 'transactions'
